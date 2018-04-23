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

