#!/usr/bin/env python
# coding=utf-8

import inkex

from inkex.bezier import csplength
from inkex import TextElement, Circle, PathElement
import string

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
        
        pars.add_argument('--adddots', default=False     )
        pars.add_argument('--addseglengths')
        
        pars.add_argument('--label_prefix', default='')
        
        pars.add_argument('--extrude', type=inkex.Boolean, default=False)
        pars.add_argument('--extrude_width', type=float, default=10.000)
        pars.add_argument('--offset', type=inkex.Boolean, default=False)
        pars.add_argument('--offset_distance', type=float, default=1.000)
        pars.add_argument('--textsize', default="10px")

    def effect(self):
        
        # inkscape 1.2 and above uses different code for document units
        
        # inkex __version__ was added just before 1.2, hence needing an error
        # catch to determine the inkscape version being used
        try:
                 if float(inkex.__version__[:3]) >= 1.2:
                   viewport_code = True
                   
                 else:
                   viewport_code = False
                  
        except Exception:
                 
                 viewport_code = False
        
        
        
        # Calculate the unit factor depending on the inkscape version
        # unittouu is not officially depreciated but is not recommended
        # The output of unittouu has changed in the past.
        
        if viewport_code == False:
        
          #############################
          # inkscape 1.1 code block
          prec = int(self.options.precision)
          scale = self.svg.unittouu('1px')  # convert to document units
          factor = 1.0

          if self.svg.get('viewBox'):
            factor = self.svg.scale / self.svg.unittouu('1px')

          factor *= scale / self.svg.unittouu('1' + self.options.unit)
          
        
        else:
          
          #inkscape 1.2 and newer
          prec = int(self.options.precision)
          scale = self.svg.viewport_to_unit(
            "1" + self.svg.document_unit
          )  # convert to document units
          factor = self.svg.unit_to_viewport(1, self.options.unit)

        

        
        

        # loop over all selected paths
        filtered = self.svg.selection.filter(inkex.PathElement)
        
        #how far to move path from the top of the bounding box
        nudge = 15
        
        if not filtered:
            raise inkex.AbortExtension(_("Please select at least one path object."))
        
        for node in filtered:
            
            csp = node.path.transform(node.composed_transform()).to_superpath()
                        
            slengths, stotal = csplength(csp)
            
            # convert segment lengths into user defined units.
            slengths_uu = []
            cumulative = [0]
            count = 0
            for number in slengths[0]:
                 length_user_unit = round(number * factor, prec)
  
                 slengths_uu.append(length_user_unit)
                 
                 count += number
                 
                 cumulative.append(round(count * factor,prec))
          
            # Position the new line at the top left corner of the bounding box
            # otherwise if you have multiple paths selected they can overlap
            # when using a fixed position.
            x_initial, y_initial = node.bounding_box().minimum
            y_initial = y_initial - nudge # nudge it slightly away from the bounding box
            
            
            # SVG code for the first point position
            single_line_init = 'M ' +  str(x_initial) + ' ' + str(y_initial) + ' ' 
            
            # Draw a horizontal line relative to the previous one the length of
            # the segment
            single_line_svg = ""
   
            for i in slengths[0]:
                single_line_svg =  single_line_svg + "h "+ str(i) + " "
              
            svg_code = single_line_init + single_line_svg       
      
            if self.options.extrude == True:
               # Convert width unit to document units
               extrude_w_doc_u = self.options.extrude_width / factor
               
               # Calculate the code for the other side of the extruded rectangle
               rev_line_svg = ""
               
               for i in list(reversed(slengths[0])):
                   rev_line_svg =  rev_line_svg + "h "+ str(-i) + " "
                  
               # Make the path into the full extruded rectangle
               svg_code = single_line_init + single_line_svg +" v " + str(-extrude_w_doc_u) + rev_line_svg + " z"
            
            
            # Make the actual path for the unrolled path.
            my_path = PathElement()

            # copy style from the original path
            my_path.style.update(node.style)
            
            # to set the style manually:
            #my_path.style['stroke'] = 'blue'
            # or update style from dictionary 
            #my_style = {'fill': 'red', 'stroke-width': '2px'}           
           
            my_path.set('d', svg_code)
            
           
            # add path to current layer
            current_layer = self.svg.get_current_layer()
            current_layer.append(my_path)
            
            # Probably a neater way to do this, but for now just replace what is
            # being passed to the add_dot function
            if self.options.addseglengths=="yessegcum":
                slengths_uu = cumulative
            

            if not self.options.adddots=="no" or not self.options.addseglengths =="no":
                
                # Add dots and labels to the original path
                self.add_dot(node, slengths_uu)
                
                # Temporary path to ensure dots are only added to the unrolled
                # line, not the entire way around the path if it has been
                # extruded
                single_line = PathElement()
                single_line.set('d', single_line_init + single_line_svg)
                current_layer.append(single_line)
                               
                self.add_dot(single_line, slengths_uu)
                
                # delete the temporary path when finished
                single_line.delete()
                
            
            if self.options.offset == True & self.options.extrude == True:
                
                # Convert offset to document units
                off_val = self.options.offset_distance / factor
                
                # Initial point, including offset
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
        elem = TextElement(x=str(x), y=str(y))
        elem.text = str(text)
        elem.style = {
            "font-size": self.svg.unittouu(self.options.textsize),
            "fill-opacity": "1.0",
            "stroke": "none",
            "font-weight": "normal",
            "font-style": "normal",
            "fill": "#000000ff",
        }
        return elem            
       
    # adapted from the Number Nodes extension
    def add_dot(self, node: inkex.PathElement, seglengths):

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
                    r=str(self.svg.unittouu(15) / 2),
                )
            )
            circle.style = style
            
            

            if self.options.adddots == "num":
                 nodeLabel = str(1+step)
                
            elif self.options.adddots == "alpha":
                 nodeLabel = string.ascii_uppercase[step]
            else:
                nodeLabel = "ddd"
            
            
            if not self.options.adddots == "no" and self.options.addseglengths=="no":
                #
                #dot_text  = self.options.label_prefix + str( 1 + step )
                dot_text  = self.options.label_prefix + nodeLabel
            else:
                # ugly hack to avoid errors when looking for a non-existent segment length for the last node.
                try:
                     
                     if not self.options.adddots == "no" and not self.options.addseglengths =="no":
                         dot_text = self.options.label_prefix + nodeLabel +": "+ str(seglengths[step]) + self.options.unit
                     else:
                         dot_text = self.options.label_prefix + str(seglengths[step]) + self.options.unit
                except Exception:
                    dot_text=""
                    pass
            
            num_group.append(
                self.add_text(
                    x + (self.svg.unittouu(self.options.textsize) / 2),
                    y - (self.svg.unittouu(self.options.textsize) / 2),
                    dot_text,
                )
            )

           
if __name__ == "__main__":
    MeasureLength().run()
