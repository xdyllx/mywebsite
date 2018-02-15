/**
 * Created by XuDongyi on 2017/11/28.
 */
function find() {

    inputField = document.getElementById("search_text");
    var arr = new Array();
    for (var i = 0; i < 3; i++) {
          arr.push(i);
     }

    set(arr);
}
function set(arr) {

    var size = arr.length;
    completeDiv = document.getElementById("popup");
    TableBody = document.getElementById("table_body");
    Table = document.getElementById("table");
    setOffsets();
    var row, cell, txtNode;
    for (var i = 0; i < size; i++) {
        var nextNode = arr[i];
        row = document.createElement("tr");
        cell = document.createElement("td");

        cell.onmouseout = function() {this.className='mouseOver';};
        cell.onmouseover = function() {this.className='mouseOut';};//鼠标悬停或离开选项时颜色变化
        cell.setAttribute("bgcolor", "#FFFAFA");
        cell.setAttribute("border", "0");
        cell.onclick = function() { populate(this); } ;  //鼠标点击选项给输入框赋值

        txtNode = document.createTextNode(nextNode);
        cell.appendChild(txtNode);
        row.appendChild(cell);
        TableBody.appendChild(row);
    }
}
function setOffsets() {
    var end = inputField.offsetWidth;
    var left = calculateOffsetLeft(inputField);
    var top = calculateOffsetTop(inputField) + inputField.offsetHeight;
    completeDiv.style.border = "black 1px solid";
    completeDiv.style.left = left + "px";
    completeDiv.style.top = top + "px";
    Table.style.width = end + "px";
}

function calculateOffsetLeft(field) {
  return calculateOffset(field, "offsetLeft");
}

function calculateOffsetTop(field) {
  return calculateOffset(field, "offsetTop");
}

function calculateOffset(field, attr) {
  var offset = 0;
  while(field) {
    offset += field[attr];
    field = field.offsetParent;
  }
  return offset;
}
function populate(cell) {//点击为文本框赋值
    inputField.value = cell.firstChild.nodeValue;
    clearNames();
}
function clear() {
    if(TableBody){
         var ind = TableBody.childNodes.length;
         for (var i = ind - 1; i >= 0 ; i--) {
             TableBody.removeChild(TableBody.childNodes[i]);
         }
         completeDiv.style.border = "none";
    }
}