/**
 * Created by XuDongyi on 2017/11/14.
 */

$(document).ready(function() {
    var chartcolor = [window.chartColors.blue, window.chartColors.green,
                    window.chartColors.yellow, window.chartColors.red];
    var labels = ['看过', '在看', '搁置', '抛弃'];

    function getCookie(c_name)
    {
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
     }


     function get_choice()
     {
        var choice = new Array();
         var count = 0;
         for(var i=1;i<5;i++)
         {
             var tmp = $("#inlineCheckbox"+i.toString())[0].checked;
             if(tmp == true)
                 count ++;
             choice.push(tmp);
         }
         return [choice, count];
     }

     $("#Confirm").click(function(){
        var info = get_choice();
        choice = info[0];
        count = info[1];
        if(count == 0)
            alert("至少选中一个！");
         else
        {
            $.ajaxSetup({
                headers: { "X-CSRFToken": getCookie("csrftoken") }
            });
            var id = ($("button.updateInfo").attr('name'));
            $.post("/bgm/refreshInfo/", {'id': id, 'choice': choice, 'cookie':document.cookie}, function(ret){
            //res = $.parseJSON(jQuery(ret).text());
            if (ret.status == "success") {
                barChartData.datasets = [];
                choice = ret.choice;

                for(var i = 0;i<4;i++)
                {
                    if(choice[i] == 'true')
                    {
                        var collect = {
                            label: labels[i],
                            backgroundColor: color(chartcolor[i]).alpha(0.5).rgbString(),
                            borderColor: chartcolor[i],
                            borderWidth: 1,
                            data: ret.distri[i]
                        };
                        barChartData.datasets.push(collect);
                    }

                }

                window.myBar.update();
                // initToastr();
                // var $toast = toastr['success']('删除成功');
            }
            else {
                alert("unknown error");
            }
        })
        }
     });
   //"更新数据"按钮被点击时的响应
    $("button.updateInfo").click(function() {
        var id = ($(this).attr('name'));
        var info = get_choice();
        choice = info[0];
        count = info[1];

        if(count == 0)
        {
            choice = [true, false, false, true];
        }

        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        $("#loading").removeClass('hidden');
        $.post("/bgm/updateInfo/", {'id': id, 'choice': choice}, function(ret){
            //res = $.parseJSON(jQuery(ret).text());
            if (ret.status == "success") {
                barChartData.datasets = [];
                choice = ret.choice;

                for(var i = 0;i<4;i++)
                {
                    if(choice[i] == 'true')
                    {
                        var collect = {
                            label: labels[i],
                            backgroundColor: color(chartcolor[i]).alpha(0.5).rgbString(),
                            borderColor: chartcolor[i],
                            borderWidth: 1,
                            data: ret.distri[i]
                        };
                        barChartData.datasets.push(collect);
                    }

                }

                $("#time_content").html("最后一次更新于"+ret.time);
                $("#loading").addClass('hidden');
                //alert("更新完毕");
                window.myBar.update();

            }
            else {
                $("#loading").addClass('hidden');
                alert("未知错误");
            }

        });

    });
});

