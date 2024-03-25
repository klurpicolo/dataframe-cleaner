import { Box } from "@mui/material";
import {
  MaterialReactTable,
  useMaterialReactTable,
} from "material-react-table";
import { useMemo } from "react";

const DisplayDataFrame = ({ data, schema }) => {
  const columns = useMemo(() => schema, [schema]);

  const memoizedData = useMemo(() => data, [data]);

  const table = useMaterialReactTable({
    columns,
    data: memoizedData, // Use the memoized data
    renderTopToolbarCustomActions: ({ table }) => (
      <Box
        sx={{
          display: "flex",
          gap: "16px",
          padding: "8px",
          flexWrap: "wrap",
        }}
      />
    ),
  });

  return <MaterialReactTable table={table} />;
};

export default DisplayDataFrame;
