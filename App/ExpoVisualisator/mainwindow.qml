import QtQuick 2.4

Rectangle {
    id: mainRec
    width: 480 
    height: 320

    Component.onCompleted:{
                            for (var i = 0; i != 3; i++)
                            {
                                console.log( i )
                                var component = Qt.createComponent("storage.qml");
                                if (component.status == Component.Ready) {
                                    var childRec = component.createObject(mainRec);
                                    childRec.x = i*childRec.width + i*10
                                    childRec.y = 50
                                    childRec.children[1].text = "!!!!"
                                }
                            }
    }
}
