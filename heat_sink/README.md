# Heat Sink Class Module

## Description

<p>Python module for heat sink design.</p>
<p>Contains class structure for heat sink design calculations.</p>

### Classes
```
Abstract:
    HeatSink
        Primary parent object to major subtypes of heat sink classes.
    StraightHeatSink
        For use with heat sinks with a straight designs..
        Subclass of HeatSink. Parent to concrete heat sink classes.
    PinHeatSink (Planned)
        For use with heat sinks with pin designs.
        Subclass of HeatSink. Parent to concrete heat sink classes.

Concrete:
    StrRectHeatSink
        Straight rectangular fin profile heat sink.
        Subclass of StraightHeatSink.
    StrTriHeatSink
        Straight triangular fin profile heat sink.
        Subclass of StraightHeatSink.
    StrParaHeatSink
        Straight parabolic fin profile heat sink.
        Subclass of StraightHeatSink.
    PinRectHeatSink (Planned)
        Rectangular pin fin profile heat sink.
        Subclass of PinHeatSink.
    PinTriHeatSink (Planned)
        Triangular pin fin profile heat sink.
        Subclass of PinHeatSink.
    PinParaSharpHeatSink (Planned)
        Parabolic pin fin profile with sharp tip heat sink.
        Subclass of PinHeatSink.
    PinParaBluntHeatSink (Planned)
        Parabolic pin fin profile with blunt tip heat sink.
        Subclass of PinHeatSink.
```
### Functions
```
suggest_fin_length(hx_coeff, fin_type, fin_thk, return_type='df', verbose=True)
    Calculate suggested fin lengths for a given material, fin type, and fin thickness.
```

## IMPORTANT

<p><strong>THIS IS AN EDUCATIONAL TOOL AND MUST NOT BE USED FOR REAL ENGINEERING APPLICATIONS</strong></p>
  
## Authors

[Chris Ponsdomenech](https://github.com/pons-dev)

## References
    Cengel, Y.A. & Ghajar, A.J., (2015).
        Heat and Mass Transfer: Fundamentals & Applications, 5th Ed.
        McGraw Hill-Education, New York, NY.
    Engineering ToolBox, (2005). 
        Metals, Metallic Elements and Alloys - Thermal Conductivities. [online] 
        Available at: https://www.engineeringtoolbox.com/thermal-conductivity-metals-d_858.html 
        [Accessed 21 Dec 2021].
