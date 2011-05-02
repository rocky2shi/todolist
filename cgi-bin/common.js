


/*
 *  功能：重写alert()，方便调试
 *  编写：Rocky 2009-12-07
 */
function Alert(/* 可变参数 */)
{
    Alert.i = (Alert.i || 0) + 1;
    alert('----------[' + Alert.i + ']----------\r\n' + '******[' + [].slice.call(arguments).join(']\r\n******[') + ']');
}

/*
 *  功能：根据控件id返回控件对象；
 */
function GetObj(id)
{
    return document.getElementById(id);
}

/*
 * 功能：创建处理对象
 * 编写：Rocky 2009-11-28
 */
function CreateXmlRequest()
{
    var xmlHttp;
    if (window.ActiveXObject)
    {
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    else if (window.XMLHttpRequest)
    {
        xmlHttp = new XMLHttpRequest();
    }
    else
    {
        alert("LoadCatchphrase::() 出错");
        return null;
    }
    return xmlHttp;
}

/*
 * 功能：发送请求到server（固定为POST方式）
 * 编写：Rocky 2009-12-02 17:23:39
 * 注意：调用函数前，应考滤content是否需要 encodeURIComponent()
 */
function SubmitToServer(url, content, callback)
{
    var xmlHttp = CreateXmlRequest();
    var method = "post";
    var asyn = true; // 默认（true）为异步处理返回的数据

    if("" == url || null == xmlHttp)
    {
        alert("SaveToServer()中出错");
        return;
    }

    // 发送请求
    function Send()
    {
        // 使用了随机数，使每次请求都刷新缓存；
        url += "?" + (Math.random() + "").substr(2) + "&";

        // 发送
        xmlHttp.onreadystatechange = Deal;
        xmlHttp.open(method, url, asyn); // true 为异步处理返回的数据
        xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xmlHttp.send(content);
    }

    // 处理返回的数据
    function Deal()
    {
        if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
        {
            // alert( decodeURIComponent(xmlHttp.responseText) );
            if(typeof callback == 'function')
            {
                callback(xmlHttp.responseText);
            }
        }
    }

    // 执行
    Send();
}
