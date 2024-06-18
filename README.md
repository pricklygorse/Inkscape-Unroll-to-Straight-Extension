Visit [www.myogtutorials.com](http://www.myogtutorials.com) if you are interested in making your own outdoor gear, using this extension or otherwise!

# Inkscape-Unroll-to-Straight-Extension

Unroll a path/shape into a straight line, maintaining the node spacings that were on the original path. Segments can be straight or bezier curves. Optionally you can add extrude and offset (e.g. add width and seam allowance) to the path.

Has been tested most on Inkscape 1.2 and 1.3. *Should* work on 1.1, but I recommend updating. Inkscape has improved so much.

![](images/summary.png)

## Example Video

[unrollextensionvideo.webm](https://github.com/pricklygorse/Inkscape-Unroll-to-Straight-Extension/assets/39905403/1b19756e-08b5-47b0-9c85-f10724993742)


## Installation

Add the .inx and .py files to your Inkscape user extensions folder. You can find this by opening Inkscape Preferences (Edit-Preferences) and selecting the System tab. Restart Inkscape and the extension will appear under Extensions - Prickly Gorse - Unroll Path to Straight Path.

I plan to release more related extensions soon, which will all be placed under the Prickly Gorse heading.

## Usage

Select your path (or multiple individual paths) and run the extension (Extensions - Prickly Gorse - Unroll Path to Straight Path).

Shapes need to be converted to paths (Object - Object to Path).

The extension can either generate a new straight path with the nodes at the same spacings, number the nodes, label segment lengths, extrude the line to a 2D shape, and add an offset to the extruded shape. You can chose the units, decimal precision, and label prefixes.

![](images/lineexamples.png)

![](images/extrude%20offset.png)




This produces a line slightly above the original path's bounding box that is the total length of the path, with nodes placed the same distances along as on the original path. You can generate either a single line (A), a line and an extra group with numbered nodes (B) or labeled segment lengths in the units of your choice (C). Using the Cumulative Segment Lengths label option is handy for marking out on fabric/paper without needing to print the image itself.

You can add a label prefix, for example if making a top and bottom line.

Numbered nodes are useful if you can't remember which node aligns with which on the original shape. If you have drawn the original path in the wrong order and don't like your starting node, chose your new starting node and use the 'Break Path at Selected Nodes' tool, then re-run the extension. Or trace over your old shape with a new path, which is a bit more reliable if you want to keep it a closed shape.


The extrude and offset features allow you to generate a full middle panel (gusset) with a seam allowance with almost zero effort. Select 'Extrude', and choose your bag width and seam allowance width.

From here you could add a marker style to the nodes for easy alignment with the side panel when sewing.



## Another example: Top Tube Bag

![](images/example2.png)

## Known Issues

Adding offset (seam allowance) to the original shape is still a bit experimental, and the offset path can sometimes be inside the original shape, or the ticks might be instead. You might need to reverse the path. Alignment marks are always added perpendicular to the path, so sharp corners will have two marks.

Sometimes the generated paths might be placed on the wrong position on the canvas, depending on how you selected the path within groups. If this happens, exit out of the group, and reselect. Don’t use CTRL+click to select into groups before running the extension.

## Prickly Gorse / MYOG tutorials Sewing Guides

I wrote this to assist with making sewing patterns for bike and backpacking bags. Bit of a shameless plug, but if you are interested in sewing your own outdoor gear without making your own patterns, check out  [www.myogtutorials.com](http://www.myogtutorials.com) for MYOG sewing focused site (patterns and articles), [www.payhip.com/pricklygorse](http://www.payhip.com/pricklygorse) where my sewing guides are hosted, or [www.pricklygorsegear.com](http://www.pricklygorsegear.com) for my handmade bags website.

You can also donate at this [link](https://www.paypal.com/donate/?business=WBEASYMGED4X8) if you find it useful :)

## Acknowledgements

The code is built upon the Measure Path and Number Nodes extensions that come pre-installed with Inkscape. Huge thanks to the authors of those extensions, and everyone who has contributed to the Inkscape project as a whole. Support open source!

------------------------------------------------------------------------
