weui.tab('#tab',{
		defaultIndex: 0,
		onChange: function(index){
			console.log(index);
		}
});

weui.tab('#navbar',{
		defaultIndex: 0,
		onChange: function(index){
			console.log(index);
		}
});

/* 图片手动上传 */
var uploadCount = 0;
var uploadCustomFileList = [];
weui.uploader('#uploader', {
   url: '',
   auto: false,
   type: 'file',
   fileVal: 'fileVal',
   compress: {
       width: 1600,
       height: 1600,
       quality: .8
   },
   onBeforeQueued: function(files) {

       if(["image/jpg", "image/jpeg", "image/png", "image/gif"].indexOf(this.type) < 0){
           weui.alert('请上传图片');
           return false; // 阻止文件添加
       }
       if(this.size > 10 * 1024 * 1024){
           weui.alert('请上传不超过10M的图片');
           return false;
       }
       if (files.length > 1) { // 防止一下子选择过多文件
           weui.alert('最多只能上传1张图片');
           return false;
       }
       if (uploadCount + 1 > 1) {
           weui.alert('只能上传1张图片');
           return false;
       }

       ++uploadCount;

       // return true; // 阻止默认行为，不插入预览图的框架
   },
   onQueued: function(){
	   uploadCustomFileList.push(this);

   }
});

// 缩略图预览
document.querySelector('#uploaderFiles').addEventListener('click', function(e){
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
                var index;
                for (var i = 0, len = uploadCustomFileList.length; i < len; ++i) {
                    var file = uploadCustomFileList[i];
                    if(file.id == id){
                        index = i;
                        break;
                    }
                }
                if(index !== undefined) uploadCustomFileList.splice(index, 1);
				uploadCount = 0;
                target.remove();
                gallery.hide();
            });
        }
    });
});



document.querySelector("#show-actions").addEventListener("click",function(){
	weui.actionSheet([
     {
         label: '拍照',
		 className:'color-primary',
         onClick: function () {
             console.log('拍照');
         }
     }, {
         label: '从相册选择',
		 className:'color-success',
         onClick: function () {
             console.log('从相册选择');
         }
     }, {
         label: '其他',
         onClick: function () {
             console.log('其他');
         }
     }
	 ], [
		 {
			 label:'取消',
			 onClick: function () {
				 console.log('取消');
			 }
		 }
	 ], {
		 className: '',
		 onClose:function(){
			 console.log('关闭');
		 }
	 });
});

