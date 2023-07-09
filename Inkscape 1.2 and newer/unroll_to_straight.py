#!/usr/bin/env python
# coding=utf-8
# inkscape 1.2

import inkex

from inkex.bezier import csplength
from inkex import TextElement, Circle, PathElement

class MeasureLength(inkex.EffectExtension):
   
    
    def add_arguments(self, pars):
        pars.add_argument('--tab')
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
            '-d', 
            '--adddots',
            default='no',
            help='Add numbered dots to both old and new path?',
        )
        
        pars.add_argument('--label_prefix', default='')
        
        pars.add_argument('--extrude', type=inkex.Boolean, default=False)
        pars.add_argument('--extrude_width', type=float, default=10.000)
        pars.add_argument('--offset', type=inkex.Boolean, default=False)
        pars.add_argument('--offset_distance', type=float, default=1.000)

    def effect(self):
        
       
        # get number of digits
        prec = int(self.options.precision)
        scale = self.svg.viewport_to_unit(
            "1" + self.svg.document_unit
        )  # convert to document units

        factor = self.svg.unit_to_viewport(1, self.options.unit)

        # loop over all selected paths
        filtered = self.svg.selection.filter(inkex.PathElement)
        
        nudge = 15
        
        if not filtered:
            raise inkex.AbortExtension(_("Please select at least one path object."))
        for node in filtered:
            
            csp = node.path.transform(node.composed_transform()).to_superpath()
                        
            slengths, stotal = csplength(csp)
            
            # convert segment lengths into user defined units.
            multiplied = []
            for number in slengths[0]:
                 multiplied.append(round(number * factor, prec))
          
 
            # Position the new line at the top left corner of the bounding box
            # otherwise if you have multiple paths selected they'll overlap
            # when using a fixed position.
            x_initial, y_initial = node.bounding_box().minimum
            y_initial = y_initial - nudge # nudge it slightly away from the bounding box
            
                
            single_line_init = 'M ' +  str(x_initial) + ' ' + str(y_initial) + ' ' 
            
            single_line_svg = ""
   
            
            for i in slengths[0]:
                single_line_svg =  single_line_svg + "h "+ str(i) + " "
              
                
            svg_code = single_line_init + single_line_svg       
      
            if self.options.extrude == True:
            
               extrude_w_doc_u = self.options.extrude_width / factor
               rev_line_svg = ""
               
               for i in list(reversed(slengths[0])):
                   rev_line_svg =  rev_line_svg + "h "+ str(-i) + " "
                  
               svg_code = single_line_init + single_line_svg +" v " + str(-extrude_w_doc_u) + rev_line_svg + " z"
            
            #####end extrude code block
            
            
            my_path = PathElement()

            # copy style from the original path
            my_path.style.update(node.style)
            
            # to set the style manually:
            #my_path.style['stroke'] = 'blue'
            # or update style from dictionary 
            #my_style = {'fill': 'red', 'stroke-width': '2px'}           
           
            my_path.set('d', svg_code     )
            
           
            # add path to current layer
            current_layer = self.svg.get_current_layer()
            current_layer.append(my_path)
                  
        
            
            
            if not self.options.adddots=="no":
                
                self.add_dot(node, multiplied)
                
                # Temporary path for adding labelled dots only to one side if extruded
                single_line = PathElement()
                single_line.set('d', single_line_init + single_line_svg  )
                current_layer.append(single_line)
                               
                self.add_dot(single_line, multiplied)
                
                # delete the temporary path when finished
                single_line.delete()
                
            
            if self.options.offset == True & self.options.extrude == True:
                
                off_val = self.options.offset_distance / factor
                
                single_line_init = 'M ' +  str(x_initial - off_val) + ' ' + str(y_initial + off_val) + ' h ' + str(off_val)
                
                svg_code = (single_line_init 
                            + single_line_svg 
                            + " h " 
                            + str(off_val)
                            + " v "
                            + str( (2*-off_val) - extrude_w_doc_u)
                            + " h " 
                            + str(-off_val)
                            + rev_line_svg
                            + str(-off_val)
                            +" z"
                            )
                my_path = PathElement()

                # copy style from the original path
                my_path.style.update(node.style)
                #my_path.style['stroke'] = 'blue'
                
                my_path.set('d', svg_code     )

                # add path to current layer
                current_layer = self.svg.get_current_layer()
                current_layer.append(my_path)
                
                
                
            
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
                dot_text  = self.options.label_prefix + str( 1 + step )
            else:
                # ugly hack to avoid errors when looking for a non-existent segment length for the last node.
                try:
                     if self.options.adddots == "yesBoth":
                         dot_text = self.options.label_prefix + str(step + 1) +": "+ str(seglengths[step]) + self.options.unit
                     else:
                         dot_text = self.options.label_prefix + str(seglengths[step]) + self.options.unit
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
