# Heat Sink Class Module

## Description

<p>
Python module for heat sink design.<br>
Contains class structure for heat sink objects.<br>
Used to determine performance of various heat sink profile designs.<br>
</p>

## IMPORTANT

<p><strong>THIS IS AN EDUCATIONAL TOOL AND MUST NOT BE USED FOR REAL ENGINEERING APPLICATIONS</strong></p>

### Classes

<img src="https://github.com/pons-dev/hxc_designer/blob/master/heat_sink/resources/obj_structure.png?raw=true" width=30% height=30%>

<p>
Individual classes are provided for each type of heat sink profile (e.g. straight rectangular fin profile heat sinks). Each heat sink profile can be grouped in under a general profile with shared design equations. For example, straight rectangular, triangular, and parabolic fin profile heat sinks have shared equations for straight profile heat sinks. As such, the class of each heat sink profile inherits a general profile abstract class (e.g. StraightHeatSink). Several design equations and attributes are universal to all heat sink profiles, thus each general profile inherits a parent HeatSink class. This class also defines all client interactions with objects for specific heat sink profiles.
</p>

```
Abstract:
    HeatSink
        Primary parent object to major subtypes of heat sink classes.
    StraightHeatSink
        For use with heat sinks with straight profile designs.
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

### Class Methods and Attributes

<p>
The purpose of the classes in this module is to calculate heat transfer parameters for various heat sink designs. The following public class attributes and methods are universal across all heat sinks objects and allow the user to extract meaningful information for each design.
</p>

```
Methods:
    hx(temp_base, temp_env, rtype=list)
        Calculates rate of heat transfer of the heat sink.

Attributes:
    fin_efficiency
        Value of fin efficiency.
        nu_fin = Q_fin_actual / Q_fin_max_ideal
    fin_effectiveness
        Ratio comparing rate of heat transfer with the fins present vs not presesnt.
        epsilon_fin = Q_fin / Q_nofin
    overall_fin_effectiveness
        Accounts for exposed base area in fin effectiveness calculations.
        epsilon_fin_overall = Q_fin_total / Q_nofin
```

### General Functions
```
suggest_fin_length(hx_coeff, fin_type, fin_thk, return_type='df', verbose=True)
    Calculate suggested fin lengths for a given material, fin type, and fin thickness.
```

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
