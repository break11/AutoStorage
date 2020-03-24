/*
  Проект "Управление блоком питания"
  Автор
    Сибилев А.С.
  Описание
    В зависимости от параметра мы включаем или отключаем блок питания.
    Если вызываем с помощью powerControl file on, то блок включается,
    есди powerControl file off - выключается
*/
#include <QCoreApplication>
#include <QtSerialPort/QSerialPort>
#include <QtSerialPort/QSerialPortInfo>
#include <QDebug>
#include <iostream>

//Напряжение, до которого заряжать, в 0.1В
#define VOLTAGE_CHARGE 432 //43.2В

//Максимальный ток заряда, в А
#define CURRENT_MAX    100 //100А

//Характеристики блока питания
//Важно!!!!!!!!!!! Категорически важно выставить здесь правильные значения
// так как значения выходного тока и напряжения устанавливаются в процентах
// от максимальных значений блока питания
#define VOLTAGE_POWER  800 //80В
#define CURRENT_POWER  170 //170А

//===========================================================================================================
//                                   Утилиты

//!
//! \brief storeInt16be Запись целого 16bit в буфер байтов старшими вперед
//! \param buf          Буфер, в который нужно произвести запись
//! \param val          Значение, которое нужно записать
//!
void storeInt16be( char *buf, int val ) {
  buf[0] = static_cast<char>((val >> 8) & 0xff);
  buf[1] = static_cast<char>((val) & 0xff);
  }



//!
//! \brief readInt16be Чтение целого 16bit из буфера старшими вперед
//! \param buf         Буфер, из которого производится чтение
//! \return            Прочитанный результат
//!
int readInt16be( const char *buf ) {
  int val = buf[0];
  val <<= 8;
  val |= buf[1] & 0xff;
  return val;
  }



//!
//! \brief persent вычисление значения процентов в формате источника питания
//!                исходя из максимального и значения
//! \param value   Значение, процент которого нужно вычислить
//! \param max     Максимальное значение, процент ОТ которого нужно вычислить
//! \return        Результирующий процент, упакованный в формате источника:
//!                старший байт - целая часть, младший байт - дробная, в 1/256 значениях
//!
int persent( int value, int max ) {
  //Вычисляем целую часть
  int integer = value * 100 / max;
  //Вычисляем дробную часть
  int fractional = (value * 100000 / max) % 1000 * 256 / 1000;
  //Возвращаем целую и дробную части
  return (integer << 8) | (fractional);
//  qDebug() << ((integer << 8) | (fractional));
//  return 0;
  }



//===========================================================================================================
//                                   Интерфейс к блоку питания

/*!
   \brief The PowerBank class представляет собой интерфейс к блоку питания

   Управление блоком питания осуществляется через запись-чтение так называемых "объектов". Объекты
   пронумерованы и имеют каждый свой формат. Полный перечень объектов - в руководстве. Ниже - краткая выдержка:
   объект данные             описание
   50     int16              Установить напряжение
   51     int16              Установить ток
   71     int16 int16 int16  Прочитать текущее значение "напряжение", "ток", "мощность" соответственно

   Значения передаются специфично - в процентах от максимальных значений источника.
   Старший байт представляет собой целую часть, а младший - дробную часть выраженную в 1/256 частях
 */
class PowerBank {
    QSerialPort mPort;
  public:
    PowerBank( const QString fname );

    //!
    //! \brief isValid Возвращает состояние порта
    //! \return        true - если порт успешно открыт, false - в противном случае
    //!
    bool isValid() const;

    //!
    //! \brief send     Формирует команду-запрос, включая контрольную сумму и отправляет блоку питания
    //! \param isQuery  Формат команды-запроса: либо запрос, либо простая отправка
    //! \param obj      Код объекта, которому отправляется запрос
    //! \param data     Дополнительные данные для запроса или 0, если данных нету
    //! \param dataLen  Длина дополнительных данных или длина данных в ответе, если формируем запрос
    //!
    bool send( bool isQuery, int obj, char *data, int dataLen );


    //!
    //! \brief send1int Отправляет объекту одно значение
    //! \param obj      Объект, которому отправляется значение
    //! \param val      Значение, которое отправляется объекту
    //! \return         true - если отправка проведена успешно, false - в противном случае
    //!
    bool send1int( int obj, int val );


    //!
    //! \brief read    чтение из блока питания
    //! \param dest    буфер для прочитанных данных, он должен быть достаточной длины для размещения dataLen данных
    //! \param dataLen максимальный размер читаемых данных
    //! \param factLen фактический размер прочитанных данных
    //! \return        true когда чтение проведено успешно и прошли все проверки, false в противном случае
    //!
    bool read( char *dest, int dataLen, int &factLen );

    //!
    //! \brief query   выполняет запрос на получение информации от объекта и получает этот ответ
    //! \param obj     код объекта, которому отправляется запрос и из которого получается ответ
    //! \param dest    буфер для прочитанных данных, он должен быть достаточной длины для размещения dataLen данных
    //! \param dataLen максимальный размер читаемых данных
    //! \param factLen фактический размер прочитанных данных
    //! \return        true когда чтение проведено успешно и прошли все проверки, false в противном случае
    //!
    bool query( int obj, char *dest, int dataLen, int &factLen );

    //!
    //! \brief query3int выполняет запрос на получение трех значений из объекта
    //! \param obj       код объекта, которому отправляется запрос и из которого получается ответ
    //! \param val       значение полученное из объекта, если все прошло удачно
    //! \return          true когда чтение проведено успешно и прошли все проверки, false в противном случае
    //!
    bool query3int( int obj, int &val1, int &val2, int &val3 );

  private:
    //!
    //! \brief error Функция предназначена для сохранения или вывода сообщения об ошибке
    //! \param str   Сообщение об ошибке
    //! \return      Всегда возвращает false
    //!
    bool error( const QString str );


    //!
    //! \brief readWithWait Прочитать данные из канала, при необходимости ждать появления данных
    //! \param dest         Буфер для данных
    //! \param len          Длина читаемых данных
    //! \return             true - если данные прочитаны успешно и false - если тайм-аут
    //!
    bool readWithWait( char *dest, int len );
  };







PowerBank::PowerBank(const QString fname) :
  mPort(fname)
  {
  if( !mPort.open( QIODevice::ReadWrite ) ) {
    qDebug() << "Serial error" << mPort.error();
    }
  else {
    //Настроить порт
    mPort.setBaudRate( QSerialPort::Baud9600 );
    mPort.setParity( QSerialPort::OddParity );
    mPort.setStopBits( QSerialPort::OneStop );
    mPort.setDataBits( QSerialPort::Data8 );
    }
  }



bool PowerBank::isValid() const
  {
  return mPort.isOpen();
  }




bool PowerBank::send(bool isQuery, int obj, char *data, int dataLen)
  {
  char buf[22]; //Буфер максимального размера для команды

  buf[0] = static_cast<char>( (dataLen - 1) |  //Длина команды
           0x10 | //Сообщение от компьютера к устройству, если наооборот - то должно быть 0
           0 |    //Сообщение определенному устройству
           (isQuery ? 0x40 : 0xc0) );   //Отправить данные
  buf[1] = 1; //Узел с устройством, для RS232 - не актуально
  buf[2] = static_cast<char>(obj); //Код объекта

  //Дополнительные данные
  int i = 3;
  if( data ) {
    while( dataLen ) {
      buf[i] = data[i-3];
      dataLen--;
      i++;
      }
    }

  //Считаем КС как простую сумму всех байтов посылки
  int sum = 0;
  for( int k = 0; k < i; k++ )
    sum += (buf[k] & 0xff);

  //Разместить КС в конце посылки
  storeInt16be( buf + i, sum );
  i += 2;

  //Выполнить передачу
  return mPort.write( buf, i ) == i;
  }





bool PowerBank::send1int(int obj, int val)
  {
  //Буфер для хранения данных
  char buf[2];
  storeInt16be( buf, val );
  return send( false, obj, buf, 2 );
  }





bool PowerBank::read(char *dest, int dataLen, int &factLen)
  {
  if( !mPort.bytesAvailable() && !mPort.waitForReadyRead(2000) )
    return error("No power bank asnwer");

  char buf[23];

  if( mPort.read( buf, 1 ) != 1 )
    return error("Can't read power bank answer");

  //Извлекаем фактическую длину дополнительных данных
  factLen = (buf[0] & 0xf) + 1;

  //Проверяем некоторые условия сообщения
  if( (buf[0] & 0x10) != 0 || (buf[0] & 0xc0) != 0x80 )
    return error( QString("Answer byte not equal for waiting %1").arg(static_cast<int>(buf[0] & 0xff)) );

  if( factLen > dataLen )
    return error( QString("Fact data lenght larger than available buffer") );

  //Читаем нужное количество байт
  if( !readWithWait( buf + 1, 2 + 2 + factLen ) )
    return error( QString("Can't read data bytes %1 %2").arg(factLen).arg(static_cast<int>(buf[0] & 0xff)) );

  //Проверим контрольную сумму
  //Сначала ее вычисляем
  int sum = 0;
  for( int i = 0; i < factLen + 3; i++ )
    sum += (buf[i] & 0xff);

  std::cout << "sum: " << sum << std::endl;
  std::cout << "Read: ";
  for( int i = 0; i < factLen + 5; i++ )
    std::cout << static_cast<int>(buf[i] & 0xff) << ", ";
  std::cout << std::endl;

  //Теперь сравниваем
  if( readInt16be(buf + factLen + 3) != sum )
    //Ошибка сравнения КС
    return error( "CS not equal to calculated" );


  //Все прошло гладко, можно вернуть прочитанные данные
  memcpy( dest, buf + 3, static_cast<size_t>(factLen) );

  return true;
  }





bool PowerBank::query(int obj, char *dest, int dataLen, int &factLen)
  {
  if( !send( true, obj, nullptr, dataLen ) )
    return error( "Can't send query" );
  return read( dest, dataLen, factLen );
  }




bool PowerBank::query3int(int obj, int &val1, int &val2, int &val3 )
  {
  //Буфер для приема результата
  char buf[6];
  int factLen = 0;
  bool res = query( obj, buf, 6, factLen );
  if( !res || factLen != 6 )
    return error( "Fail query 3 int" );

  //Парсить ответ
  val1 = readInt16be( buf );
  val2 = readInt16be( buf + 2 );
  val3 = readInt16be( buf + 4 );
  return true;
  }




bool PowerBank::error(const QString str)
  {
  qWarning() << str;
  return false;
  }




bool PowerBank::readWithWait(char *dest, int len)
  {
  while( mPort.bytesAvailable() || mPort.waitForReadyRead(3000) ) {
    //Пытаемся прочитать байты
    int factLen = static_cast<int>( mPort.read( dest, len ) );
    if( factLen < 1 ) return false;
    //Продвинуть указатель и уменьшить счетчик
    dest += factLen;
    len  -= factLen;
    //Если счетчик уменьшился до нуля, то все байты прочитаны и возврат
    if( len == 0 )
      return true;
    }
  //Тайм-аут ожидания данных
  return false;
  }




//===========================================================================================================
//                                   Точка входа


int main(int argc, char *argv[])
  {
  QCoreApplication a(argc, argv);
  std::cout << "Usage: powerControl file on - for power on, and" << std::endl
            << "       powerControl file off - for power off" << std::endl
            << "where file - com port file" << std::endl;

  //Вывести список доступных портов
  std::cout << "Available port names:" << std::endl;
  auto portList = QSerialPortInfo::availablePorts();
  for( auto info : portList )
    std::cout << info.portName().toLatin1().constData() << std::endl;
  std::cout << "---------------------" << std::endl;

  if( argc != 3 ) {
    std::cout << "Wrong argument number. See usage above." << std::endl;
    return 1;
    }

  //Создать канал взаимодействия с блоком питания
  PowerBank pb( a.arguments().at(1) );
  if( !pb.isValid() ) {
    std::cout << "Can't open serial port." << std::endl;
    return 2;
    }

  //Прочитать из блока питания его название
  char powerBankTitle[17];
  int factLen;
  if( !pb.query( 0, powerBankTitle, 16, factLen ) ) {
    std::cout << "Fail to read power bank title. Its may be not power bank." << std::endl;
    return 3;
    }

  //Название прочитано успешно, покажем его
  powerBankTitle[factLen] = 0;
  std::cout << "Successfully connected to power bank: " << powerBankTitle << std::endl;

  //Состояние включенности
  if( !pb.query( 54, powerBankTitle, 2, factLen ) ) {
    std::cout << "Fail to read power bank on-off status." << std::endl;
    return 3;
    }

  if( a.arguments().at(2) == QString("on") ) {

    //Теперь установим выходное напряжение
    if( !pb.send1int( 50, persent( VOLTAGE_CHARGE, VOLTAGE_POWER ) ) ) {
      std::cout << "Fail to set voltage." << std::endl;
      return 4;
      }

    //Устанавливаем выходной ток
    if( !pb.send1int( 51, persent( CURRENT_MAX, CURRENT_POWER ) ) ) {
      std::cout << "Fail to set current." << std::endl;
      return 5;
      }

    //Включаем
    if( !pb.send1int( 54, 0x101 ) ) {
      std::cout << "Fail to switch on." << std::endl;
      return 6;
      }
    if( !pb.query( 54, powerBankTitle, 2, factLen ) ) {
      std::cout << "Fail to read power bank on-off status." << std::endl;
      return 3;
      }

    std::cout << "Power seems to be on" << std::endl;
    }

  else if( a.arguments().at(2) == QString("off") ) {

    //Выключаем
    if( !pb.send1int( 54, 0x100 ) ) {
      std::cout << "Fail to switch off." << std::endl;
      return 7;
      }
    if( !pb.query( 54, powerBankTitle, 2, factLen ) ) {
      std::cout << "Fail to read power bank on-off status." << std::endl;
      return 3;
      }

    std::cout << "Power seems to be off" << std::endl;
    }

  else {
    std::cout << "Wrong second argument: " << argv[2] << std::endl;
    return 8;
    }

  //Успешное завершение
  return 0;
  }




