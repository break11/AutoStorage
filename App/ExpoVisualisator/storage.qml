import QtQuick 2.4

Rectangle {
    id: box
    color: "blue"
    width: 100; height: 100

    MouseArea { 
            id: r
            anchors.fill: parent
            onClicked: expo_vis.slot1("SSS")
            // onClicked: console.log( "!!!" )
        }

    Text {
            id: txt
            font.pointSize: 18
            color: "white"
        }
}