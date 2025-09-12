import React from "react";
import type { Point, Equation } from "../../../type.ts";
import DrawingOptions from "./DrawingOptions";
import EquationList from "./EquationList";
import PointList from "./PointList";

interface RightSidebarProps {
  equationData: Equation[];
  setEquationData: React.Dispatch<React.SetStateAction<Equation[]>>;
  points: Point[];
  setPoints: React.Dispatch<React.SetStateAction<Point[]>>;
  highlightedEquationIds: string[];
  setHighlightedEquationIds: React.Dispatch<React.SetStateAction<string[]>>;
  highlightedPointIndices: number[];
  setHighlightedPointIndices: React.Dispatch<React.SetStateAction<number[]>>;
  hiddenEquationIds: string[];
  setHiddenEquationIds: React.Dispatch<React.SetStateAction<string[]>>;
  hiddenPointIndices: number[];
  setHiddenPointIndices: React.Dispatch<React.SetStateAction<number[]>>;
  clearPoints: () => void;
  allowLine: boolean;
  setAllowLine: React.Dispatch<React.SetStateAction<boolean>>;
  allowCurve: boolean;
  setAllowCurve: React.Dispatch<React.SetStateAction<boolean>>;
  allowCircle: boolean;
  setAllowCircle: React.Dispatch<React.SetStateAction<boolean>>;
  setSelectedPoints: React.Dispatch<React.SetStateAction<Point[]>>;
  handleFindIntersections: () => void;
  handleClearIntersections: () => void;
}

const RightSidebar: React.FC<RightSidebarProps> = (props) => {
  const {
    equationData,
    setEquationData,
    highlightedEquationIds,
    setHighlightedEquationIds,
    hiddenEquationIds,
    setHiddenEquationIds,
    points,
    setPoints,
    highlightedPointIndices,
    setHighlightedPointIndices,
    hiddenPointIndices,
    setHiddenPointIndices,
    clearPoints,
    allowLine,
    setAllowLine,
    allowCurve,
    setAllowCurve,
    allowCircle,
    setAllowCircle,
    setSelectedPoints,
    handleFindIntersections,
    handleClearIntersections
  } = props;

  return (
    <div
      style={{
        width: "370px",
        marginLeft: "20px",
        borderLeft: "1px solid #ccc",
        paddingLeft: "10px",
        height: "690px",
      }}
    >
      <button onClick={handleFindIntersections}>Find Intersections</button>
      <button onClick={handleClearIntersections}>
          Clear Intersections
      </button>
      <DrawingOptions
        allowLine={allowLine}
        setAllowLine={setAllowLine}
        allowCurve={allowCurve}
        setAllowCurve={setAllowCurve}
        allowCircle={allowCircle}
        setAllowCircle={setAllowCircle}
        setSelectedPoints={setSelectedPoints}
      />

      <EquationList
        equations={equationData}
        setEquations={setEquationData}
        highlighted={highlightedEquationIds}
        setHighlighted={setHighlightedEquationIds}
        hidden={hiddenEquationIds}
        setHidden={setHiddenEquationIds}
      />

      <PointList
        points={points}
        setPoints={setPoints}
        highlighted={highlightedPointIndices}
        setHighlighted={setHighlightedPointIndices}
        hidden={hiddenPointIndices}
        setHidden={setHiddenPointIndices}
        clearPoints={clearPoints}
      />
    </div>
  );
};

export default RightSidebar;
