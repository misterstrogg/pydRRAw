var fixtures={};
fixtures.DEMO = [
  {w: 1, h: 1, x: 9, y: 2}
];

// Enable Node module
// if (typeof(require) == 'function') {
//   for (var k in fixtures) {
//       exports[k] = fixtures[k];
//         }
//         }
var DemoGrid = {
  currentSize: 3,
  currentHeight: 3,
  buildElements: function($gridContainer, items) {
    var item, i;
    for (i = 0; i < items.length; i++) {
      item = items[i];
      $item = $(
        '<li>' +
          '<div class="inner">' +
            '<div class="controls">' +
              '<a href="#zoom1" class="resize" data-size="1">1x</a>' +
              '<a href="#zoom2" class="resize" data-size="2">2x</a>' +
              '<a href="#zoom3" class="resize" data-size="3">3x</a>' +
            '</div>' +
          '</div>' +
        '</li>'
      );
      $item.attr({
        'data-w': item.w,
        'data-h': item.h,
        'data-x': item.x,
        'data-y': item.y,
        'data-alttext': item.u
      });
      $gridContainer.append($item);
    }
  },
  resize: function(size) {
    if (size) {
      this.currentSize = size;
    }
    $('#grid').gridList('resize', this.currentSize);
  },  
  reheight: function(height) {
    if (height) {
      this.currentSize = height;
    }
    $('#grid').gridList('reheight', this.currentHeight);
  },

  flashItems: function(items) {
    // Hack to flash changed items visually
    for (var i = 0; i < items.length; i++) {
      (function($element) {
        $element.addClass('changed')
        setTimeout(function() {
          $element.removeClass('changed');
        }, 0);
      })(items[i].$element);
    }
  }
};

$(window).resize(function() {
  DemoGrid.resize();
});

$(function() {
  DemoGrid.buildElements($('#grid'), fixtures.DEMO);

  $('#grid').gridList({
    rows: DemoGrid.currentSize,
    widthHeightRatio: 264 / 294,
    heightToFontSizeRatio: 0.25,
    onChange: function(changedItems) {
      DemoGrid.flashItems(changedItems);
    }
  });
  $('#grid li .resize').click(function(e) {
    e.preventDefault();
    var itemElement = $(e.currentTarget).closest('li'),
        itemSize = $(e.currentTarget).data('size');
    $('#grid').gridList('resizeItem', itemElement, itemSize);
  });
  $('#grid li .reheight').click(function(e) {
    e.preventDefault();
    var itemElement = $(e.currentTarget).closest('li'),
        itemHeight = $(e.currentTarget).data('height');
    $('#grid').gridList('reheightItem', itemElement, itemHeight);
  });
  $('.add-row').click(function(e) {
    e.preventDefault();
    DemoGrid.resize(DemoGrid.currentSize + 1);
  });
  $('.remove-row').click(function(e) {
    e.preventDefault();
    DemoGrid.resize(Math.max(1, DemoGrid.currentSize - 1));
  });
});
