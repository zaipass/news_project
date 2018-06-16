function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    var action = "";

    // 收藏
    $(".collection").click(function () {
        // 判断是否登录 登录-> 事件收藏 ; 未登录 -> 提示
        action = "collection";
        var news_id = $(this).attr("data-news");
        var params = {
            "action": action,
            "news_id": news_id
        };
        $.get("/collection", params, function(data){
            if(data.errno == "0"){
                alert(data.errmsg);
                $(".collection").hide();
                $(".collected").show();
            }else {
                alert(data.errmsg);
            }
        });
       
    });

    // 取消收藏
    $(".collected").click(function () {
        action = "collected";
        var news_id = $(this).attr("data-news");
        var params = {
            "action": action,
            "news_id": news_id
        };
        $.get("/collection", params, function(data){
            if(data.errno == "0"){
                alert(data.errmsg);
                $(".collected").hide();
                $(".collection").show();
            }else {
                alert(data.errmsg);
            }
        });
     
    });

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var newsId = $(this).attr("data-newsId");

        var content = $(".comment_input").val();

        var params = {
            "news_id": newsId,
            "content": content
        };

        $.ajax({
            url:"/comments",
            type:'post', // 请求方法
            data:JSON.stringify(params), // 请求参数
            contentType:'application/json', // 请求数据类型
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function(response){
                // alert(response.errmsg);
                if(response.errno == "0"){
                    alert(response.errmsg);
                    var content = '<div class="comment_list">';
                    if (response.data.user.avatar_url){
                        var img_content = '<div class="person_pic fl"> ' +
                            '<img src="'+response.data.user.avatar_url+'" alt="用户图标">' +
                            ' </div>';
                    }else {
                        var img_content = '<div class="person_pic fl"> ' +
                            '<img src="../../static/news/images/worm.jpg" alt="用户图标"> </div>';
                    }
                    var comment_content = '<div class="user_name fl">'+ response.data.user.nick_name +'</div> ' +
                        '<div class="comment_text fl">'+response.data.comment.content+' </div>' +
                        '<div class="comment_time fl">'+response.data.comment.create_time+'</div>' +
                        '<a href="javascript:;" class="comment_up has_comment_up fr">' +
                        ''+response.data.comment.like_count+'</a>' +
                        '<a href="javascript:;" class="comment_reply fr">回复</a> ' +
                        '<from class="reply_form fl" data-parentId='+response.data.comment.id+
                        ' data-newsId='+response.data.comment.news_id+' > ' +
                        '<textarea  class="reply_input"></textarea> ' +
                        '<input type="submit" name="" value="回复" class="reply_sub fr"> ' +
                        '<input type="reset" name="" value="取消" class="reply_cancel fr"> </from> </div>';
                    $('.comment_input').html("");
                    $(".comment_list_con").prepend(content+img_content+comment_content);
                }else {
                    alert(response.errmsg);
                }
            }
        });

    });

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            var commentId = $this.attr("data-commentId");
            var com_action = "";
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                com_action = "unlike";

                var cparams = {
                    "action": com_action,
                    "comment_id": commentId
                };

                $.ajax({
                    url:"/liked",
                    type:'post', // 请求方法
                    data:JSON.stringify(cparams), // 请求参数
                    contentType:'application/json', // 请求数据类型
                    headers:{'X-CSRFToken':getCookie('csrf_token')},
                    success:function(response){
                        if(response.errno == "0"){
                            $this.html(response.liked);
                            $this.removeClass('has_comment_up');
                        }else{
                            alert(response.errmsg);
                        }
                    }
                })

            }else {
                com_action = "liked";

                var cparams = {
                    "action": com_action,
                    "comment_id": commentId
                };

                $.ajax({
                    url:"/liked",
                    type:'post', // 请求方法
                    data:JSON.stringify(cparams), // 请求参数
                    contentType:'application/json', // 请求数据类型
                    headers:{'X-CSRFToken':getCookie('csrf_token')},
                    success:function(response){
                        if(response.errno == "0"){
                            $this.html(response.liked);
                            $this.addClass('has_comment_up');
                        }else{
                            alert(response.errmsg);
                        }
                    }
                })

            }
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            // alert('回复评论')
            var newsId = $(this).parent().attr("data-newsId");

            // 注意: >>>> $('reply_sub').val() 是只能获取一次表单内容
            var content = $(this).prev().val();

            var parentId = $(this).parent().attr("data-parentId");

            var params = {
                "news_id": newsId,
                "content": content,
                "parent_id": parentId
            };

            $.ajax({
                url:"/comments",
                type:'post', // 请求方法
                data:JSON.stringify(params), // 请求参数
                contentType:'application/json', // 请求数据类型
                headers:{'X-CSRFToken':getCookie('csrf_token')},
                success:function(response){
                    if(response.errno == "0"){
                        var content = '<div class="comment_list">';
                        if (response.data.user.avatar_url){
                            var img_content = '<div class="person_pic fl"> ' +
                                '<img src="'+response.data.user.avatar_url+'" alt="用户图标">' +
                                ' </div>';
                        }else {
                            var img_content = '<div class="person_pic fl"> ' +
                                '<img src="../../static/news/images/worm.jpg" alt="用户图标"> </div>';
                        }
                        var comment_content = '<div class="user_name fl">'+ response.data.user.nick_name +'</div> ' +
                            '<div class="comment_text fl">'+response.data.comment.content+' </div>' +
                            '<div class="reply_text_con fl"> ' +
                            '<div class="user_name2">'+response.data.comment.parent.user.nick_name+'</div> ' +
                            '<div class="reply_text">'+response.data.comment.parent.content+'</div> </div>' +
                            '<div class="comment_time fl">'+response.data.comment.create_time+'</div>' +
                            '<a href="javascript:;" class="comment_up has_comment_up fr">' +
                            ''+response.data.comment.like_count+'</a>' +
                            '<a href="javascript:;" class="comment_reply fr">回复</a> ' +
                            '<from class="reply_form fl" data-parentId='+response.data.comment.id+
                            ' data-newsId='+response.data.comment.news_id+' > ' +
                            '<textarea  class="reply_input">'+response.data.comment.news_id+'.....' +
                            ''+response.data.comment.id+'</textarea> ' +
                            '<input type="submit" name="" value="回复" class="reply_sub fr"> ' +
                            '<input type="reset" name="" value="取消" class="reply_cancel fr"> </from> </div>';
                        $(".reply_input").val('');
                        $(".comment_list_con").prepend(content+img_content+comment_content);
                    }else {
                        alert(response.errmsg);
                    }
                }

            });
        }
    });

        // 关注当前新闻作者
    $(".focus").click(function () {
        // 发布此新闻用户id
        var authorId = $(this).attr("data-authorId");
        var pam = {
            "author_id":authorId
        };

        $.ajax({
            url: "/follow",
            type: 'post', // 请求方法
            data: JSON.stringify(pam), // 请求参数
            contentType: 'application/json', // 请求数据类型
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success:function(response){
                if(response.errno == "0"){
                    alert(response.errmsg);
                }else{
                    alert(response.errmsg);
                }
            }
        })

    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
});