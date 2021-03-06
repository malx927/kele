
$(function() {
    //FastClick.attach(document.body);

});


//首页图片轮播
function setImageUrl(){
    $.ajax({
      type: 'GET',
      url: '/wechat/api/swiperimagelist',
      dataType: 'json',
      timeout: 5000,
      context: $('.swiper-wrapper'),
      success: function(data){
        console.log(data);
        imgList ='';
          $.each(data.results,function(index,item){
              imgList += '<div class="swiper-slide"><img src="'+ item.image +'" data-link="'+ item.url +'"></div>';

          });
          $('.swiper-wrapper').append(imgList);
          var mySwiper = new Swiper ('.swiper-container', {
                initialSlide :0,
                direction: 'horizontal',
                speed:2000,
                autoplay : {
                    delay:3000,
                    disableOnInteraction: false,
                },
                loop: true,
                pagination: {
                    el: '.swiper-pagination',
                    clickable :true,
                  },
                observer:true,
                observeParents:true,
                on:{
                    tap:function(event){
                       url = event.target.attributes["data-link"].nodeValue;
                       if (url.length > 7){
                           window.location.href =  event.target.attributes["data-link"].nodeValue ;
                       }
                    },
                },
        });

      },
      error: function(xhr, type,error){
          console.log(type,error);
      }
    });
}

////性别图标
function getSexImage(item){
        var seximg = item.sex;
        if( seximg != null && seximg == '公') {
            seximg = '<i class="icon iconfont icon-man14 male"></i> ';
        }
        else{
            seximg = '<i class="icon iconfont icon-female3 female"></i> ';
        }
        return seximg;
}


///* 图片手动上传 */
//var uploadCount = 0;
//var uploadCustomFileList = [];
//weui.uploader('#uploader', {
//   url: '',
//   auto: false,
//   type: 'file',
//   fileVal: 'fileVal',
//   compress: {
//       width: 1600,
//       height: 1600,
//       quality: .8
//   },
//   onBeforeQueued: function(files) {
//
//       if(["image/jpg", "image/jpeg", "image/png", "image/gif"].indexOf(this.type) < 0){
//           weui.alert('请上传图片');
//           return false; // 阻止文件添加
//       }
//       if(this.size > 10 * 1024 * 1024){
//           weui.alert('请上传不超过10M的图片');
//           return false;
//       }
//       if (files.length > 1) { // 防止一下子选择过多文件
//           weui.alert('最多只能上传1张图片');
//           return false;
//       }
//       if (uploadCount + 1 > 1) {
//           weui.alert('只能上传1张图片');
//           return false;
//       }
//
//       ++uploadCount;
//
//       // return true; // 阻止默认行为，不插入预览图的框架
//   },
//   onQueued: function(){
//	   uploadCustomFileList.push(this);
//       $("#id_picture").value= this
//   }
//});

$(function(){
    var tmpl = '<li class="weui-uploader__file" style="background-image:url(#url#)"></li>',
        //$gallery = $("#gallery"), $galleryImg = $("#galleryImg"),
        $uploaderInput = $("#id_picture");
        $uploaderFiles = $("#uploaderFiles");

        $uploaderInput.on("change", function(e){
            var src, url = window.URL || window.webkitURL || window.mozURL, files = e.target.files;
            $('#uploaderFiles li').remove();
            for (var i = 0, len = files.length; i < len; ++i) {
                var file = files[i];

                if(file.size > 6 * 1024 * 1024) {
                    weui.alert('请上传不超过6M的图片');
                    return false;
                }
                if (url) {
                    src = url.createObjectURL(file);
                } else {
                    src = e.target.result;
                }

                $uploaderFiles.append($(tmpl.replace('#url#', src)));
            }
        });

    });


// 缩略图预览

$('#uploaderFiles').on('click', function(e){
    var target = e.target;

    while(!target.classList.contains('weui-uploader__file') && target){
        target = target.parentNode;
    }
    if(!target) return;

    var url = target.getAttribute('style') || '';
    var id = target.getAttribute('data-id');

    if(url){
        url = url.match(/url\((.*?)\)/)[1].replace(/"/g, '');
    }
    var gallery = weui.gallery(url, {
        onDelete: function(){
            weui.confirm('确定删除该图片？', function(){
                $("#id_picture").val('');
                target.remove();
                gallery.hide();
            });
        }
    });
});


$('.detail_header').on('click', function(e){
    var target = e.target;

    if(!target) return;

    var url = target.getAttribute('src') || '';

    if(!url) return;
    var gallery = weui.gallery(url);
    $('.weui-gallery__del').remove();
    $('.weui-gallery span').html('');
});


function showing(){
    var wins = weui.loading('处理中...');
    return true;
}

function getCurrDate(){
    var date = new Date();
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    if (month < 10) {
        month = "0" + month;
    }

    if (day < 10) {
        day = "0" + day;
    }
    return year + "-" + month + "-" + day;
}