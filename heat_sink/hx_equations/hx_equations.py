"""Help on hx_equations package:
Name
    hx_equations

Description
    Heat sink heat transfer equation module
    =========================================
    hx_equations is a Python module used for thermal calculations involving heatsinks.
    Its aim is to provide a basis for heat sink design optimization.
    It is a part of the hxc_designer module.

Classes:
    HeatTransfer

Functions:
    functions_example(input1, input2)

Misc Variables:
    __version__
    var1


References:
    Cengel, Y.A. & Ghajar, A.J., (2015).
        Heat and Mass Transfer: Fundamentals & Applications, 5th Ed.
        McGraw Hill-Education, New York, NY.



"""


class HeatTransferMixin:
    def _calc_q_fin_single(
        self, temp_base, temp_env, hx_coeff, fin_efficiency, fin_area_single
    ):
        """Calculate heat transfer rate for a single fin.
        Q_fin = nu_fin * h * A_fin * (temp_base - temp_env)
        Q_fin : Heat transfer rate of a single fin.
        nu_fin : Fin efficiency.
        A_fin : Surface area of a single fin.
        temp_base : Temperature of the base.
        temp_env : Temperature of the environment.

        Parameters
        ----------
        temp_base : int or float
            Temperature of the base.
        temp_env : int or float
            Temperature of the environment.

        Returns
        -------
        q_fin : float
            Heat transfer rate of a single fin.
        """
        # Q_fin = nu_fin * h * A_fin * (T_base - T_inf)
        delta_t = temp_base - temp_env
        q_fin = fin_efficiency * hx_coeff.h * fin_area_single * delta_t
        return q_fin

    def _calc_q_fin_total(
        self, temp_base, temp_env, hx_coeff, fin_efficiency, fin_area_total
    ):
        """Calculate heat transfer rate of all fin area.
        Q_fin = nu_fin * h * A_fin * (temp_base - temp_env)
        Q_fin : Heat transfer rate of all fin area.
        nu_fin : Fin efficiency.
        A_fin : Surface area of all fins.
        temp_base : Temperature of the base.
        temp_env : Temperature of the environment.

        Parameters
        ----------
        temp_base : int or float
            Temperature of the base.
        temp_env : int or float
            Temperature of the environment.

        Returns
        -------
        q_fin : float
            Heat transfer rate of all fin area.
        """
        # Q_fin = nu_fin * h * A_fin * (T_base - T_inf)
        delta_t = temp_base - temp_env
        q_fin = fin_efficiency * hx_coeff.h * fin_area_total * delta_t
        return q_fin

    def _calc_q_heat_sink(
        self,
        temp_base,
        temp_env,
        hx_coeff,
        fin_efficiency,
        fin_area_total,
        base_area_nonfin,
    ):
        """Calculate heat transfer rate of the heat sink.
        Q_heat_sink = h * (A_nonfin + nu_fin * A_fin) * (temp_base - temp_env)
        Q_heat_sink : Heat transfer rate of heat sink.
        A_nonfin : Exposed surface area of the base.
        nu_fin : Fin efficiency.
        A_fin : Surface area of all fins.
        temp_base : Temperature of the base.
        temp_env : Temperature of the environment.

        Parameters
        ----------
        temp_base : int or float
            Temperature of the base.
        temp_env : int or float
            Temperature of the environment.

        Returns
        -------
        q_heat_sink : float
            Heat transfer rate of all fin area.
        """
        # Q_fin = h * (A_nonfin + nu_fin * A_fin) * (T_base - T_inf)
        delta_t = temp_base - temp_env
        area_effective = (
            base_area_nonfin + fin_efficiency * fin_area_total
        )  # Effective surface area
        q_heat_sink = hx_coeff.h * area_effective * delta_t
        return q_heat_sink
