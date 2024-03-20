import { useMemo } from "react";
import {
  MaterialReactTable,
  useMaterialReactTable,
} from "material-react-table";

const DisplayDataFrame = ({ data, schema }) => {
  const columns = useMemo(() => schema, [schema]);

  const memoizedData = useMemo(() => data, [data]);

  const table = useMaterialReactTable({
    columns,
    data: memoizedData, // Use the memoized data
  });

  return <MaterialReactTable table={table} />;
};

export default DisplayDataFrame;
