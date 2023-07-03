#!/usr/bin/env python
# coding=utf-8
#

import inkex

from inkex.bezier import csplength
from inkex import TextElement, Circle, PathElement

class MeasureLength(inkex.EffectExtension):
   
    
    def add_arguments(self, pars):
        
        pars.add_argument(
            "-u", "--unit", default="px", help="The unit of the measurement"
        )
        pars.add_argument(
            "-p",
            "--precision",
            type=int,
            default=2,
            help="Number of significant digits after decimal point",
        )
        pars.add_argument(
            "-s",
            "--scale",
            type=float,
            default=1.0,
            help="Scale Factor (Drawing:Real Length)",
        )
        
        pars.add_argument(
            '-d', 
            '--adddots',
            default='no',
            help='Add numbered dots to both old and new path?',
        )
        

    def effect(self):
        

        # loop over all selected paths
        filtered = self.svg.selection.filter(inkex.PathElement)
        
        if not filtered:
            raise inkex.AbortExtension(_("Please select at least one path object."))
        for node in filtered:
            
            csp = node.path.transform(node.composed_transform()).to_superpath()
            
            slengths, stotal = csplength(csp)
            
            # convert segment lengths into user defined units.
           
          
            my_path = PathElement()

            # copy style from the original path
            my_path.style.update(node.style)
            
            # If you want to set the style manually:
            #my_path.style['stroke'] = 'blue'
            # update style from dictionary 
            #my_style = {'fill': 'red', 'stroke-width': '2px'}
                        
            # Position the new line at the top left corner of the bounding box
            # otherwise if you have multiple paths selected they'll overlap
            # when using a fixed position.
            x_initial, y_initial = node.bounding_box().minimum
            y_initial = y_initial - 5 # nudge it slightly away from the bounding box
            
            x_increment = x_initial
            svg_code = 'M ' + str(x_initial) + ' ' + str(y_initial) + ' ' 
            
            for i in slengths[0]:
               x_increment = x_increment + i
               svg_code = svg_code + str(x_increment) + ' ' + str(y_initial) + ' ' 
            
            my_path.set('d', svg_code     )
            
            
            # add path to current layer
            current_layer = self.svg.get_current_layer()
            current_layer.append(my_path)
            
       
            
            
           
            
            if not self.options.adddots=="no":
            
            
              # get number of digits
              prec = int(self.options.precision)
              # this and the factor line do not work on versions of inkscape earlier than 1.2
              scale = self.svg.viewport_to_unit(
                 "1" + self.svg.document_unit
              )  # convert to document units
        

              factor = self.svg.unit_to_viewport(1, self.options.unit)
        
              multiplied = []
              for number in slengths[0]:
                 multiplied.append(round(number * factor * self.options.scale, prec))
            
            
              self.add_dot(node, '')
              self.add_dot(my_path, multiplied)
            
            
            
    # slightly modified from the Number Nodes extension
    def add_text(self, x, y, text):
        """Add a text label at the given location"""
        elem = TextElement(x=str(x), y=str(y))
        elem.text = str(text)
        elem.style = {
            "font-size": self.svg.unittouu(16),
            "fill-opacity": "1.0",
            "stroke": "none",
            "font-weight": "normal",
            "font-style": "normal",
            "fill": "#000000ff",
        }
        return elem            
       
    # slightly modified from the Number Nodes extension
    def add_dot(self, node: inkex.PathElement, seglengths):
        """Add a dot label for this path element"""
        group: inkex.Group = node.getparent().add(inkex.Group())
        dot_group = group.add(inkex.Group())
        num_group = group.add(inkex.Group())
        path_trans_applied = node.path.transform(node.composed_transform())
        group.transform = -node.getparent().composed_transform()

        style = inkex.Style({"stroke": "none", "fill": "#000"})
        
        for step, (x, y) in enumerate(path_trans_applied.end_points):
            circle = dot_group.add(
                Circle(
                    cx=str(x),
                    cy=str(y),
                    #replaced user defined diameter with 10 for simplicity
                    r=str(self.svg.unittouu(10) / 2),
                )
            )
            circle.style = style
                        
            if self.options.adddots == "yesNum":
                dot_text=1 + step
            else:
                # ugly hack to avoid errors when looking for a non-existent segment length for the last node.
                try:
                     dot_text = seglengths[step]
                except Exception:
                    dot_text=""
                    pass
            
            num_group.append(
                self.add_text(
                    #replaced user defined diameter with 10 for ease
                    x + (self.svg.unittouu(10) / 2),
                    y - (self.svg.unittouu(10) / 2),
                    dot_text,
                )
            )

           
if __name__ == "__main__":
    MeasureLength().run()
