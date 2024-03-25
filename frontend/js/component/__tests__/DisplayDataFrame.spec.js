import { render } from "@testing-library/react";
import React from "react";

import DisplayDataFrame from "../DisplayDataFrame";

describe("DisplayDataFrame", () => {
  const data = [
    { id: 1, name: "John", age: 30 },
    { id: 2, name: "Jane", age: 25 },
  ];

  const schema = [
    { Header: "ID", id: "1", accessor: "id" },
    { Header: "Name", id: "2", accessor: "name" },
    { Header: "Age", id: "3", accessor: "age" },
  ];

  test("renders without crashing", () => {
    render(<DisplayDataFrame data={data} schema={schema} />);
  });

  test("renders correct number of rows", () => {
    const { getAllByRole } = render(
      <DisplayDataFrame data={data} schema={schema} />,
    );
    const rows = getAllByRole("row");
    // Account for header row
    expect(rows).toHaveLength(data.length + 1);
  });
});
