#!/usr/bin/env python
# coding=utf-8

import inkex

from inkex.bezier import csplength
from inkex import TextElement, Circle, PathElement
import string


#imports for tangent
from inkex.paths import Path, Curve, Move, Line, Quadratic, move, curve, line
from inkex.transforms import Vector2d
import math
from math import atan2, degrees

from inkex import PathEffect

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
        pars.add_argument('--copy_style', type=inkex.Boolean, default=True)
        pars.add_argument('--offset_distance', type=float, default=1.000)
        pars.add_argument('--offset_shape', type=inkex.Boolean, default=False)
        pars.add_argument('--textsize', default="10px")
        pars.add_argument('--initial_n', default=1)

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
          # convert to document units
          scale = self.svg.viewport_to_unit("1" + self.svg.document_unit)  
          factor = self.svg.unit_to_viewport(1, self.options.unit)

        

        
        

        # loop over all selected paths
        filtered = self.svg.selection.filter(inkex.PathElement)
        
        
        
        if not filtered:
            raise inkex.AbortExtension(_("Please select at least one path object. Shapes need to be converted to a path using the menu option: Object - Object to Path"))
        
        
        tick_style = inkex.Style(
          {
            "stroke": "red",
            "stroke-width": self.svg.unittouu("0.5mm"),
            "fill": "none",
            #"stroke-dasharray": str(1/factor) + "," + str(1/factor)
          }
        )
        border_style = inkex.Style(
          {
            "stroke": "black",
            "stroke-width": self.svg.unittouu("0.5mm"),
            "fill": "none",
            #"stroke-dasharray": str(1/factor) + "," + str(1/factor)
          }
        )
        seamline_style = inkex.Style(
          {
            "stroke": "black",
            "stroke-width": self.svg.unittouu("0.5mm"),
            "fill": "none",
            "stroke-dasharray": "4,4"
          }
        )
        
       
        
        
        
        
        
        
        for node in filtered:
            
            # Make a group for all the generated objects
            current_layer = inkex.Group()
            self.svg.get_current_layer().append(current_layer)
            
            
            csp = node.path.transform(node.composed_transform()).to_superpath()
            slengths, stotal = csplength(csp)
            
            # convert segment lengths into user defined units.
            slengths_uu = [round(number * factor, prec) for number in slengths[0]]
            cumulative = [0]
            count = 0
            for number in slengths[0]:
                 
                 count += number
                 
                 cumulative.append(round(count * factor,prec))
          
            
          
            # Position the new line at the top left corner of the bounding box
            # otherwise if you have multiple paths selected they can overlap
            # when using a fixed position.
            x_initial, y_initial = node.bounding_box().minimum
            y_initial -= 25 # nudge it slightly away from the bounding box
            
            
            # SVG code for the first point position
            svg_code = f'M {x_initial} {y_initial} '
            svg_initial_line = ""

            #single_line_svg = ""
            ticks=""
            
            # Convert offset and extrude width to document units
            off_val = self.options.offset_distance / factor
            extrude_w_doc_u = self.options.extrude_width / factor
            
            # Draw a horizontal line relative to the previous one the length of
            # the segment
            for i in slengths[0]:
                svg_code += f'h {i} '
                svg_initial_line += f'h {i} '
                #alignment ticks
                ticks += f'v {off_val} m {i},-{off_val} '
                
            
            
            
            #svg_code = single_line_init + single_line_svg
            
            
            #add the final tick
            ticks += f'v {off_val}'
            
            #ticks_svg = single_line_init + ticks + single_line_init + "m 0," + str(-extrude_w_doc_u - off_val) + ticks
            ticks_svg = f'M {x_initial} {y_initial} {ticks} M {x_initial},{y_initial - extrude_w_doc_u - off_val} {ticks}'
            
                  
            if self.options.extrude == True:
               # Convert width unit to document units
               extrude_w_doc_u = self.options.extrude_width / factor
               
               # Calculate the code for the other side of the extruded rectangle
               rev_line_svg = ""
               
               for i in list(reversed(slengths[0])):
                   rev_line_svg +=  f"h {-i} "
                  
               # Make the path into the full extruded rectangle
               #svg_code = single_line_init + single_line_svg +" v " + str(-extrude_w_doc_u) + rev_line_svg + " z"
               svg_code += f' v {-extrude_w_doc_u} {rev_line_svg} z'
            
            # Make the actual path for the unrolled path.
            my_path = PathElement()

            
            if self.options.offset == True & self.options.extrude == True:
                #set style to match my sewing patterns
                my_path.style = seamline_style
              
            else:
               # copy style from the original path
               my_path.style.update(node.style)
            
            # to set the style manually:
            #my_path.style['stroke'] = 'blue'
            # or update style from dictionary 
            #my_style = {'fill': 'red', 'stroke-width': '2px'}           
           
            my_path.set('d', svg_code)
            
           
            # add path to current layer
            current_layer.append(my_path)
            
            # Probably a neater way to do this, but for now just replace what is
            # being passed to the add_dot function
            if self.options.addseglengths=="cumulative":
                slengths_uu = cumulative
            

            if not self.options.adddots=="no" or not self.options.addseglengths =="no":
                
                # Add dots and labels to the original path
                self.add_dot(node, slengths_uu)
                
                # Temporary path to ensure dots are only added to the unrolled
                # line, not the entire way around the path if it has been
                # extruded
                single_line = PathElement()
                single_line.set('d', f'M {x_initial} {y_initial} {svg_initial_line}')
                
                
                
                
                current_layer.append(single_line)
                               
                self.add_dot(single_line, slengths_uu)
                
                # delete the temporary path when finished
                single_line.delete()
                
            
            if self.options.offset == True & self.options.extrude == True:
                
                
                off_val = self.options.offset_distance / factor
                
                if self.options.offset_shape:
                    self.tangentlines(node,off_val)
                    self.offsetLPE(node)
                
                
                # Initial point, including offset
                svg_code = (
                    f'M {x_initial - off_val} {y_initial + off_val} h {off_val} '
                    f'{svg_initial_line} h {off_val} v {-(2 * off_val + extrude_w_doc_u)} h {-off_val} {rev_line_svg}{-off_val} z'
                )
                
   
                my_path = PathElement()

                # copy style from the original path
                #my_path.style.update(node.style)
                my_path.style = border_style
                
                my_path.set('d', svg_code     )

                # add path to current layer
                current_layer.append(my_path)
                
                my_path = PathElement()
                my_path.style = tick_style
                my_path.set('d', ticks_svg)
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
        # account for layers having transforms, so when
        # you add stuff to the document it is added relative to the layer transform,
        # not the absolute document X Y position
        path_trans_applied = node.path.transform(node.composed_transform())
        group.transform = -node.getparent().composed_transform()

        style = inkex.Style({"stroke": "none", "fill": "#000"})
        
        for step, (x, y) in enumerate(path_trans_applied.end_points):
            circle = dot_group.add(
                Circle(
                    cx=str(x),
                    cy=str(y),
                    #replaced user defined diameter with 15 for simplicity
                    r=str(self.svg.unittouu(15) / 2),
                )
            )
            circle.style = style

            if self.options.adddots == "num":
                 nodeLabel = str(step + int(self.options.initial_n))
                
            elif self.options.adddots == "alpha":
                 nodeLabel = string.ascii_uppercase[step]
            else:
                nodeLabel = ""
            
            segLabel = ""
         
            if step < len(seglengths):
                if not self.options.adddots == "no" and not self.options.addseglengths == "no":
                    segLabel = f": {seglengths[step]}{self.options.unit}"
                elif self.options.adddots == "no" and not self.options.addseglengths == "no":
                    segLabel = f"{seglengths[step]}{self.options.unit}"
            
            dot_text = self.options.label_prefix + nodeLabel + segLabel
            
            num_group.append(
                self.add_text(
                    x + (self.svg.unittouu(self.options.textsize) / 2),
                    y - (self.svg.unittouu(self.options.textsize) / 2),
                    dot_text,
                )
            )











    def tangentlines(self, node,off_val):
        
        #for node in self.svg.selection.filter(inkex.PathElement):
            
            
            
            result = Path()
    
            prev = Vector2d()
            start = None
            
                       
           
            node2 = node.copy()
            node2.path = node2.get_path().to_superpath().to_path(curves_only=True)
            
            #self.msg(node.path)
            #self.msg(node2.path)
            
            for seg in node2.path.to_relative():
    
                #self.msg("")
                
                
                if start is None:
                    start = seg.end_point(start, prev)
                    
                
                
                #self.msg((seg))
                #self.msg(dir(seg))
                
                # the superpath transform seems to make the last node the same as previous.
                # C 0 0 0 0 0, so this checks to avoid that segment
                if isinstance(seg, curve) and not (seg.dx2+seg.dx3+seg.dx4+seg.dy2+seg.dy3+seg.dy4)==0:
                    
    
                    line_length=off_val
                    
                    #if the first node is a corner node with no handle,
                    # use the second handle as the reference point 
                    if seg.dy2 == 0 and seg.dx2 == 0:
                        ang = atan2(seg.dy3 , seg.dx3 )
                        
                    else:
                        ang = atan2(seg.dy2 , seg.dx2 )
    
                    x_end =  line_length * math.cos(ang)
                    y_end =  line_length * math.sin(ang)
                    
                    
                    
                    #if the second node is a corner node with no handle,
                    # use the first handle as the reference point 
                    if seg.dy3 == seg.dy4 and seg.dx3 == seg.dx4:
                        dy3 = seg.dy2
                        dx3 = seg.dx2
                    else:
                        dy3 = seg.dy3
                        dx3 = seg.dx3
                    
                    ang2 = atan2(dy3-seg.dy4 , dx3-seg.dx4 )
                    
                    x_end2 =  line_length * math.cos(ang2)
                    y_end2 =  line_length * math.sin(ang2)
                    
                    #self.msg(degrees(ang2))
                    #self.msg(y_end2)
                    
                    result += [
                        
                        Move(prev.x, prev.y),
                        line(y_end, -x_end),
                        
    
                        #go back
                        move(-y_end, x_end),
                        
                        
                        move(seg.dx4, seg.dy4),
                        line(-(y_end2), (x_end2)),
                        
                        
                        
                        #original extension code
                        # Move(seg.x2, seg.y2),
                        # Line(prev.x, prev.y),
                        # Move(seg.x3, seg.y3),
                        # Line(seg.x4, seg.y4),
                        
                        
                        
                        
                    ]
                # elif isinstance(seg, Quadratic):
                #     result += [
                #         Move(seg.x2, seg.y2),
                #         Line(prev.x, prev.y),
                #         Move(seg.x2, seg.y2),
                #         Line(seg.x3, seg.y3),
                #     ]
                prev = seg.end_point(start, prev)
                
    
            #if not result:
            #    continue
    
            elem = node.getparent().add(inkex.PathElement())
            elem.path = result.transform(node.transform)
            elem.style = {
                "stroke-linejoin": "miter",
                "stroke-width": "0.5",
                "stroke-opacity": "1.0",
                "fill-opacity": "1.0",
                "stroke": "red",
                "stroke-linecap": "butt",
                "fill": "none",
            }




    def offsetLPE(self, node):
            
            node2 = node.copy()
            
            node2.style = {
                "stroke-linejoin": "miter",
                "stroke-width": "0.5",
                "stroke-opacity": "1.0",
                "fill-opacity": "1.0",
                "stroke": "blue",
                "stroke-linecap": "butt",
                "fill": "none",
            }
            
            self.svg.get_current_layer().append(node2)
    
            #offset is a parameter from the extension ui.
            #offset = self.options.offset
            offset_param_dict = {"update_on_knot_move": "true", 
                                      "attempt_force_join": "false", 
                                      "miter_limit": "4", 
                                      "offset": self.options.offset_distance, 
                                      "unit": self.options.unit,
                                      "linejoin_type": "miter",
                                      "lpeversion": "1.2",
                                      "is_visible": "true",
                                      "effect": "offset"}
    
            #for p in paths_element:
            effect = PathEffect()
            for key in offset_param_dict:
                effect.set(key, offset_param_dict[key])          

            self.svg.defs.add(effect)
            node2.set('inkscape:original-d', node2.attrib["d"])
            node2.set('inkscape:path-effect', effect.get_id(as_url = 1))   
            node2.pop('d')













           
if __name__ == "__main__":
    MeasureLength().run()
