var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 当主页加载完成后，立即主动的获取新闻列表数据
    updateNewsData();

    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid;

            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            updateNewsData()
        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            if (data_querying == false && cur_page <= total_page){
                data_querying = true;
                cur_page += 1;
                updateNewsData();
            }
        }
    })
});

function updateNewsData() {
    // TODO 更新新闻数据
    var params = {
        'cid':currentCid,
        'page':cur_page
        // 不需要传入per_page,因为默认10
    };

    $.get('/news/news_all', params, function (response) {
        total_page = response.context.tpage;
        if (response.errno == '0') {
            data_querying = false;
            // # 注意翻页的核心代码 , 因为当点击切换类型时候,会出现重置页数的
            if(cur_page == 1){
                $(".list_con").html("")
            }
            // 获取数据成功，使用新的数据渲染界面
            for (var i=0;i<response.context.news.length;i++) {
                var news = response.context.news[i];
                var content = '<li>';
                content += '<a href="#" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>'
                content += '<a href="#" class="news_title fl">' + news.title + '</a>';
                content += '<a href="#" class="news_detail fl">' + news.digest + '</a>';
                content += '<div class="author_info fl">';
                content += '<div class="source fl">来源：' + news.source + '</div>';
                content += '<div class="time fl">' + news.create_time + '</div>';
                content += '</div>';
                content += '</li>';
                // append表示将新的数据追加到旧的数据的后面；html表示将新的数据替换到旧的数据的后面；
                $(".list_con").append(content)
            }
        } else {
            alert(response.errmsg);
        }
    });
}
