/*
// jQuery multiSelect
//
// Version 1.0 beta
//
// Cory S.N. LaViska
// A Beautiful Site (http://abeautifulsite.net/)
// 06 April 2008
//
// Visit http://abeautifulsite.net/notebook.php?article=62 for more information
//
// Usage: $('#control_id').multiSelect( options, callback )
//
// Options:  selectAll          - whether or not to display the Select All option; true/false, default = true
//           selectAllText      - text to display for selecting/unselecting all options simultaneously
//           noneSelected       - text to display when there are no selected items in the list
//           oneOrMoreSelected  - text to display when there are one or more selected items in the list
//                                (note: you can use % as a placeholder for the number of items selected).
//                                Use * to show a comma separated list of all selected; default = '% selected'
//
// Dependencies:  jQuery 1.2 or higher (http://jquery.com/)
//                the jQuery Dimensions plugin (http://plugins.jquery.com/project/dimensions)
//
// Licensing & Terms of Use
//
// jQuery File Tree is licensed under a Creative Commons License and is copyrighted (C)2008 by Cory S.N. LaViska.
// For details, visit http://creativecommons.org/licenses/by/3.0/us/
//
*/
if(jQuery) (function($){

	$.extend($.fn, {
		multiSelect: function(o, callback) {
			// Default options
			if( !o ) var o = {};
			if( o.selectAll == undefined ) o.selectAll = true;
			if( o.selectAllText == undefined ) o.selectAllText = "Select All";
			if( o.noneSelected == undefined ) o.noneSelected = 'Select options';
			if( o.oneOrMoreSelected == undefined ) o.oneOrMoreSelected = '% selected';

			// Initialize each multiSelect
			$(this).each( function() {
				var select = $(this);
				var html = '<input type="text" readonly="readonly" class="multiSelect" value="" style="cursor: default;" />';
				html += '<div class="multiSelectOptions" style="position: absolute; z-index: 99999; display: none;">';
				if( o.selectAll ) html += '<label class="selectAll"><input type="checkbox" class="selectAll" />' + o.selectAllText + '</label>';
				$(select).find('OPTION').each( function() {
					if( $(this).val() != '' )
					    html += '<label for="'+$(select).attr('name')+'">'+$(this).html() + '</label><input type="checkbox" name="' + $(select).attr('name') + '" value="' + $(this).val() + '"'+($(this).attr('selected')?' checked="checked"':'')+' />';
				});
				html += '</div>';
				$(select).after(html);

				// Events
				$(select).next('.multiSelect').mouseover( function() {
					$(this).addClass('hover');
				}).mouseout( function() {
					$(this).removeClass('hover');
				}).click( function() {
					// Show/hide on click
					if( $(this).hasClass('active') ) {
						$(this).multiSelectOptionsHide();
					} else {
						$(this).multiSelectOptionsShow();
					}
					return false;
				}).focus( function() {
					// So it can be styled with CSS
					$(this).addClass('focus');
				}).blur( function() {
					// So it can be styled with CSS
					$(this).removeClass('focus');
				});

				// Determine if Select All should be checked initially
				if( o.selectAll ) {
					var sa = true;
					$(select).next('.multiSelect').next('.multiSelectOptions').find('INPUT:checkbox').not('.selectAll').each( function() {
						if( !$(this).attr('checked') ) sa = false;
					});
					if( sa ) $(select).next('.multiSelect').next('.multiSelectOptions').find('INPUT.selectAll').attr('checked', true).parent().addClass('checked');
				}

				// Handle Select All
				$(select).next('.multiSelect').next('.multiSelectOptions').find('INPUT.selectAll').click( function() {
					if( $(this).attr('checked') == true ) $(this).parent().parent().find('INPUT:checkbox').attr('checked', true).parent().addClass('checked'); else $(this).parent().parent().find('INPUT:checkbox').attr('checked', false).parent().removeClass('checked');
				});

				// Handle checkboxes
				$(select).next('.multiSelect').next('.multiSelectOptions').find('INPUT:checkbox').click( function() {
					$(this).parent().parent().multiSelectUpdateSelected(o);
					$(this).parent().parent().find('LABEL').removeClass('checked').find('INPUT:checked').parent().addClass('checked');
					$(this).parent().parent().prev('.multiSelect').focus();
					if( !$(this).attr('checked') ) $(this).parent().parent().find('INPUT:checkbox.selectAll').attr('checked', false).parent().removeClass('checked');
					if( callback ) callback($(this));
				});

				// Initial display
				$(select).next('.multiSelect').next('.multiSelectOptions').each( function() {
					$(this).multiSelectUpdateSelected(o);
					$(this).find('INPUT:checked').parent().addClass('checked');
				});

				// Handle hovers
				$(select).next('.multiSelect').next('.multiSelectOptions').find('LABEL').mouseover( function() {
					$(this).parent().find('LABEL').removeClass('hover');
					$(this).addClass('hover');
				}).mouseout( function() {
					$(this).parent().find('LABEL').removeClass('hover');
				});

				// Keyboard
				$(select).next('.multiSelect').keydown( function(e) {
					// Is dropdown visible?
					if( $(this).next('.multiSelectOptions').is(':visible') ) {
						// Dropdown is visible
						// Tab
						if( e.keyCode == 9 ) {
							$(this).addClass('focus').trigger('click'); // esc, left, right - hide
							$(this).focus().next(':input').focus();
							return true;
						}

						// ESC, Left, Right
						if( e.keyCode == 27 || e.keyCode == 37 || e.keyCode == 39 ) {
							// Hide dropdown
							$(this).addClass('focus').trigger('click');
						}
						// Down
						if( e.keyCode == 40 ) {
							if( !$(this).next('.multiSelectOptions').find('LABEL').hasClass('hover') ) {
								// Default to first item
								$(this).next('.multiSelectOptions').find('LABEL:first').addClass('hover');
							} else {
								// Move down, cycle to top if on bottom
								$(this).next('.multiSelectOptions').find('LABEL.hover').removeClass('hover').next('LABEL').addClass('hover');
								if( !$(this).next('.multiSelectOptions').find('LABEL').hasClass('hover') ) {
									$(this).next('.multiSelectOptions').find('LABEL:first').addClass('hover');
								}
							}
							return false;
						}
						// Up
						if( e.keyCode == 38 ) {
							if( !$(this).next('.multiSelectOptions').find('LABEL').hasClass('hover') ) {
								// Default to first item
								$(this).next('.multiSelectOptions').find('LABEL:first').addClass('hover');
							} else {
								// Move up, cycle to bottom if on top
								$(this).next('.multiSelectOptions').find('LABEL.hover').removeClass('hover').prev('LABEL').addClass('hover');
								if( !$(this).next('.multiSelectOptions').find('LABEL').hasClass('hover') ) {
									$(this).next('.multiSelectOptions').find('LABEL:last').addClass('hover');
								}
							}
							return false;
						}
						// Enter, Space
						if( e.keyCode == 13 || e.keyCode == 32 ) {
							// Select All
							if( $(this).next('.multiSelectOptions').find('LABEL.hover INPUT:checkbox').hasClass('selectAll') ) {
								if( $(this).next('.multiSelectOptions').find('LABEL.hover INPUT:checkbox').attr('checked') ) {
									// Uncheck all
									$(this).next('.multiSelectOptions').find('INPUT:checkbox').attr('checked', false).parent().removeClass('checked');
								} else {
									// Check all
									$(this).next('.multiSelectOptions').find('INPUT:checkbox').attr('checked', true).parent().addClass('checked');
								}
								$(this).next('.multiSelectOptions').multiSelectUpdateSelected(o);
								if( callback ) callback($(this));
								return false;
							}
							// Other checkboxes
							if( $(this).next('.multiSelectOptions').find('LABEL.hover INPUT:checkbox').attr('checked') ) {
								// Uncheck
								$(this).next('.multiSelectOptions').find('LABEL.hover INPUT:checkbox').attr('checked', false);
								$(this).next('.multiSelectOptions').multiSelectUpdateSelected(o);
								$(this).next('.multiSelectOptions').find('LABEL').removeClass('checked').find('INPUT:checked').parent().addClass('checked');
								// Select all status can't be checked at this point
								$(this).next('.multiSelectOptions').find('INPUT:checkbox.selectAll').attr('checked', false).parent().removeClass('checked');
								if( callback ) callback($(this));
							} else {
								// Check
								$(this).next('.multiSelectOptions').find('LABEL.hover INPUT:checkbox').attr('checked', true);
								$(this).next('.multiSelectOptions').multiSelectUpdateSelected(o);
								$(this).next('.multiSelectOptions').find('LABEL').removeClass('checked').find('INPUT:checked').parent().addClass('checked');
								if( callback ) callback($(this));
							}
						}
						return false;
					} else {
						// Dropdown is not visible
						if( e.keyCode == 38 || e.keyCode == 40 || e.keyCode == 13 || e.keyCode == 32 ) { // down, enter, space - show
							// Show dropdown
							$(this).removeClass('focus').trigger('click');
							$(this).next('.multiSelectOptions').find('LABEL:first').addClass('hover');
							return false;
						}
						//  Tab key
						if( e.keyCode == 9 ) {
							// Shift focus to next INPUT element on page
							$(this).focus().next(':input').focus();
							return true;
						}
					}
					// Prevent enter key from submitting form
					if( e.keyCode == 13 ) return false;
				});

				// Eliminate the original form element
				$(select).remove();
			});

		},

		// Hide the dropdown
		multiSelectOptionsHide: function() {
			$(this).removeClass('active').next('.multiSelectOptions').hide();
		},

		// Show the dropdown
		multiSelectOptionsShow: function() {
			// Hide any open option boxes
			$('.multiSelect').multiSelectOptionsHide();
			$(this).next('.multiSelectOptions').find('LABEL').removeClass('hover');
			$(this).addClass('active').next('.multiSelectOptions').show();

			// Position it
			var offset = $(this).offset();
			$(this).next('.multiSelectOptions').css({ top:  offset.top + $(this).outerHeight() + 'px' });
			$(this).next('.multiSelectOptions').css({ left: offset.left + 'px' });

			// Disappear on hover out
			multiSelectCurrent = $(this);
			var timer = '';
			$(this).next('.multiSelectOptions').hover( function() {
				clearTimeout(timer);
			}, function() {
				timer = setTimeout('$(multiSelectCurrent).multiSelectOptionsHide(); $(multiSelectCurrent).unbind("hover");', 250);
			});

		},

		// Update the textbox with the total number of selected items
		multiSelectUpdateSelected: function(o) {
			var i = 0, s = '';
			$(this).find('INPUT:checkbox:checked').not('.selectAll').each( function() {
				i++;
			})
			if( i == 0 ) {
				$(this).prev('INPUT.multiSelect').val( o.noneSelected );
			} else {
				if( o.oneOrMoreSelected == '*' ) {
					var display = '';
					$(this).find('INPUT:checkbox:checked').each( function() {
						if( $(this).parent().text() != o.selectAllText ) display = display + $(this).parent().text() + ', ';
					});
					display = display.substr(0, display.length - 2);
					$(this).prev('INPUT.multiSelect').val( display );
				} else {
					$(this).prev('INPUT.multiSelect').val( o.oneOrMoreSelected.replace('%', i) );
				}
			}
		}

	});

})(jQuery);
