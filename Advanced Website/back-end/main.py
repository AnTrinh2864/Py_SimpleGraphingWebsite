from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp
import numpy as np
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)
from typing import List, Dict
SUPERSCRIPTS = {
    "²": "**2",
    "³": "**3",
    "⁴": "**4",
    "⁵": "**5",
    "⁶": "**6",
    "⁷": "**7",
    "⁸": "**8",
    "⁹": "**9",
    "⁰": "**0",
}

def normalize_equation(eq: str) -> str:
    for sup, repl in SUPERSCRIPTS.items():
        eq = eq.replace(sup, repl)
    return eq

app = FastAPI()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
transformations = standard_transformations + (implicit_multiplication_application,)
# Test connection
@app.get("/ping")
def read_root():
    return {"message": "pong"}

# Model for requests
class EquationRequest(BaseModel):
    equation: str
    x_min: float = -10
    x_max: float = 10
    num_points: int = 200

@app.post("/compute")
def compute_equation(req: EquationRequest):
    try:
        # Enable implicit multiplication: 2x -> 2*x
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(req.equation.replace("^", "**"), transformations=transformations)

        x = sp.symbols("x")
        f = sp.lambdify(x, expr, "math")

        xs = np.linspace(req.x_min, req.x_max, req.num_points).tolist()
        ys = []
        for val in xs:
            try:
                ys.append(f(val))
            except Exception:
                ys.append(None)

        return {"x": xs, "y": ys, "equation": req.equation}

    except Exception as e:
        return {"error": str(e)}

class PointsRequest(BaseModel):
    points: list[tuple[float, float]]

@app.post("/fit-line")
def fit_line(req: PointsRequest):
    points = np.array(req.points)
    if len(points) != 2:
        return {"error": "Line requires exactly 2 points"}
    
    (x1, y1), (x2, y2) = points
    if x1 == x2:
        return {"error": "Vertical line not supported"}
    
    # slope + intercept
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    
    # generate data for frontend plotting
    x_vals = np.linspace(min(x1, x2) - 1, max(x1, x2) + 1, 500).tolist()
    y_vals = [(a * x + b) for x in x_vals]

    return {"a": a, "b": b, "x": x_vals, "y": y_vals}


@app.post("/fit-quadratic")
def fit_quadratic(req: PointsRequest):
    points = np.array(req.points)
    if len(points) != 3:
        return {"error": "Quadratic requires exactly 3 points"}
    
    X = np.array([[x**2, x, 1] for x, _ in points])
    y = np.array([y for _, y in points])
    
    # solve coefficients
    a, b, c = np.linalg.solve(X, y)
    
    x_vals = np.linspace(min(points[:,0]) - 1, max(points[:,0]) + 1, 500).tolist()
    y_vals = [(a * x**2 + b * x + c) for x in x_vals]
    
    return {"a": a, "b": b, "c": c, "x": x_vals, "y": y_vals}

@app.post("/fit-circle")
def fit_circle(req: PointsRequest):
    points = np.array(req.points)
    if len(points) != 2:
        return {"error": "Circle requires exactly 2 points (center, edge)"}

    (x1, y1), (x2, y2) = points

    # radius = distance between center and edge
    r = float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    # parametric circle
    theta = np.linspace(0, 2 * np.pi, 500)
    x_vals = (x1 + r * np.cos(theta)).tolist()
    y_vals = (y1 + r * np.sin(theta)).tolist()

    return {
        "h": float(x1),
        "k": float(y1),
        "r": r,
        "x": x_vals,
        "y": y_vals
    }

class Equation(BaseModel):
    id: str
    name: str   # match frontend "name"


class EquationListRequest(BaseModel):
    equations: List[Equation]


@app.post("/intersections")
def intersections(req: EquationListRequest):
    x, y = sp.symbols("x y")

    exprs = []
    for eq in req.equations:
        if "=" not in eq.name:
            return {"error": f"Equation {eq.name} must contain '='"}
        
        left, right = eq.name.split("=", 1)
        left = normalize_equation(left.strip())
        right = normalize_equation(right.strip())

        expr = sp.Eq(   
            parse_expr(left, transformations=transformations),
            parse_expr(right, transformations=transformations)
        )

        exprs.append((eq.id, expr))

    intersections = []
    for i in range(len(exprs)):
        for j in range(i + 1, len(exprs)):
            id1, e1 = exprs[i]
            id2, e2 = exprs[j]
            try:
                sols = sp.solve([e1, e2], (x, y), dict=True)

                for s in sols:
                    try:
                        x_val = s[x].evalf()
                        y_val = s[y].evalf()

                        # Only keep if numeric
                        if x_val.is_real and y_val.is_real:
                            intersections.append({
                                "x": float(x_val),
                                "y": float(y_val),
                                "from": [id1, id2]
                            })
                    except Exception:
                        continue  # skip if cannot convert
            except Exception as e:
                print(f"Failed solving {id1} & {id2}: {e}")
                continue

    return {"points": intersections}

