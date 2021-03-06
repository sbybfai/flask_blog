$(function(){
    var $modal = $('#replayModal');
    // 测试 bootstrap 居中
    $modal.on('show.bs.modal', function(){
      var $this = $(this);
      var $modal_dialog = $this.find('.modal-dialog');
      // 关键代码，如没将modal设置为 block，则$modala_dialog.height() 为零
      $this.css('display', 'block');
      $modal_dialog.css({'margin-top': Math.max(0, ($(window).height() - $modal_dialog.height()) / 2) });
    });

    $("[data-toggle='popover']").popover();
    $("table").addClass("table table-bordered table-striped");

   new Toc( 'post-body',{
        'level':3,
        'top':100,
        'class':'toc',
        'targetId':'toc'
    } );

});

function replay(id){
   $('#replayId').val(id);
   $('#replayModal').modal('show');
}

