import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from sympy import symbols, Eq, solve, nsolve, nsimplify, pi
from sympy.parsing.sympy_parser import (
    standard_transformations, implicit_multiplication_application,
    convert_xor, parse_expr
)

st.title("Graphing Calculator")

equations = st.text_input("Enter equation(s):", "sin(x), x^2")

# User inputs for multiple values
x_vals_raw = st.text_input("Enter x values (comma separated):", "")
y_vals_raw = st.text_input("Enter y values (comma separated):", "")

x_vals = [float(v.strip()) for v in x_vals_raw.split(",") if v.strip()]
y_vals = [float(v.strip()) for v in y_vals_raw.split(",") if v.strip()]

x = symbols("x")
X = np.linspace(-100, 100, 5000)

# ✅ Now supports implicit multiplication and ^ as power
transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
fig = go.Figure()

expr_list = []

# Plot each equation
for eq in equations.split(","):
    eq = eq.strip()
    if eq:
        try:
            expr = parse_expr(eq, transformations=transformations)
            expr_list.append(expr)

            f = np.vectorize(lambda t: float(expr.subs(x, t)))
            Y = f(X)
            fig.add_trace(go.Scatter(x=X, y=Y, mode="lines", name=str(expr)))

            # 🔴 Only plot user x values if given
            if x_vals:
                for xv in x_vals:
                    y_from_x = expr.subs(x, xv)
                    if y_from_x.is_real:
                        fig.add_trace(go.Scatter(
                            x=[xv], y=[float(y_from_x)],
                            mode="markers+text",
                            name=f"x={xv} on {expr}",
                            text=[f"({xv:.2f}, {float(y_from_x):.2f})"],
                            textposition="top center",
                            marker=dict(size=10, color="teal", symbol="circle")
                        ))

            # 🟢 Only plot user y values if given
            if y_vals:
                for yv in y_vals:
                    sol = solve(Eq(expr, yv), x)
                    for s in sol:
                        if s.is_real:
                            try:
                                xs = float(s.evalf())
                                fig.add_trace(go.Scatter(
                                    x=[xs], y=[yv],
                                    mode="markers+text",
                                    name=f"y={yv} on {expr}",
                                    text=[f"({xs:.2f}, {yv:.2f})"],
                                    textposition="top center",
                                    marker=dict(size=10, color="red", symbol="diamond")
                                ))
                            except:
                                pass

        except Exception as e:
            st.error(f"Error parsing '{eq}': {e}")

# 🔍 Button to find ALL intersections
# --- Show Intersections ---
# 🔧 Domain controls for intersection search
st.subheader("Intersection Scan Range")
col1, col2, col3 = st.columns(3)

with col1:
    scan_min = st.number_input("Min x", value=-10.0, step=1.0)
with col2:
    scan_max = st.number_input("Max x", value=10.0, step=1.0)
with col3:
    scan_points = st.number_input("Sample points", value=100, step=50)

# Store intersections globally so both graph + table can use them
intersections = []

if st.button("Show Intersections"):
    intersections.clear()
    X_scan = np.linspace(scan_min, scan_max, int(scan_points))
    for i in range(len(expr_list)):
        for j in range(i + 1, len(expr_list)):
            eq1, eq2 = expr_list[i], expr_list[j]

            try:
                Y1 = np.array([eq1.subs(x, xv).evalf() for xv in X_scan], dtype=float)
                Y2 = np.array([eq2.subs(x, xv).evalf() for xv in X_scan], dtype=float)
                diff = Y1 - Y2

                for k in range(len(X_scan) - 1):
                    if diff[k] * diff[k+1] < 0:  # sign change
                        try:
                            sol = nsolve(eq1 - eq2, x, (X_scan[k] + X_scan[k+1]) / 2)
                            xs_val = float(sol)
                            ys_val = float(eq1.subs(x, xs_val))
                            if scan_min <= xs_val <= scan_max:
                                pt = (xs_val, ys_val)
                                if pt not in intersections:  # avoid duplicates
                                    intersections.append(pt)

                                    fig.add_trace(go.Scatter(
                                        x=[xs_val], y=[ys_val],
                                        mode="markers+text",
                                        name="Intersection",
                                        text=[f"({xs_val:.2f}, {ys_val:.2f})"],
                                        textposition="bottom center",
                                        marker=dict(size=12, color="orange", symbol="star")
                                    ))
                        except Exception:
                            pass
            except Exception:
                pass
# Layout
fig.update_layout(
    dragmode="pan",
    xaxis=dict(title="x", range=[-10, 10]),
    yaxis=dict(title="y", range=[-10, 10], autorange=False)
)

st.plotly_chart(fig, use_container_width=True)
