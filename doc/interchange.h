#ifndef INTERCHANGE_H
#define INTERCHANGE_H
/*
Формат сообщения:
  (заголовок)(данные)
Формат заголовка:
  (номер сообщения - десятичное число 3 знакa)~(время - шестнадцатиричное число 8 знаков, сервер время не отсылает)~(идентификатор сообщения - 2 знака)~
Формат данных:
  (последовательность полей, разделенных знаком ^)
Формат поля:
  (любая последовательность знаков за исключением знаков ~ и ^)

Все сообщения должны соответствовать приведенному формату.
Вводим стадию инициализации:
  - при подключении агент посылает серверу сообщение HW с полями:
    (тип агента - текст)
    (идентификатор агента - десятичное число)
    например, 003~01234567~HW~cartV1^101

  - в ответ сервер посылает агенту свое сообщение HW без данных
    например, 003~~HW~
  с этого момента стартует цикл обмена сообщениями.
  Повторный прием сервером сообщения HW также должен подтверждаться ответным HW.
  Номера сообщений в сообщениях HW игнорируются.

Цикл обмена сообщениями состоит из отправки и приема сообщений:
  - при отправке сообщения ожидается ответное подтверждение, если оно получено, то отправляется следующее сообщение (при наличии),
    если в ответ подтверждения с нужным номером не получено, то посылка повторяется

    например, отправляем  004~01234568~BS~30^5.2V^5.2V^5.2V^4.1A^4.2A
    ожидаем подтверждения 004~~AC~


  - при приеме сообщения отправляется подтверждение (всегда), если предыдущее сообщение было с этим-же номером, то сообщение игнорируется
    (подтверждение все-равно должно отсылаться)
    например, приняли 005~~PD~
    отправили подтверждение 005~01234569~AC~

    Для реализации этого механизма должна храниться переменная "номер последнего принятого сообщения" ассоциированная с устройством,
    с которым осуществляется связь. При включении программы этой переменной присвоить минус1, чтобы не было совпадения ни с каким номером.
    В дальнейшем, эта переменная модифицируется только при отправке подтверждения.

Текстовое сообщение, идентификатор TX, в данных - текст:
    например 006~01234570~TX~ пример текстового сообщения

Сообщение типа "внимание", идентификатор WR, в данных - текст:
    например 007~01234571~WR~###warning! command OP ignored in error state###

Сообщение типа "ошибка", идентификатор ER, в данных следующие поля:
    - поле класса ошибки - десятичный номер
    - поле текста ошибки

    например 008~01234572~ER~01~*** Error! Loading box fail ***
*/
#endif // INTERCHANGE_H
