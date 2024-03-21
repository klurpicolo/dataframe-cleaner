import { useMemo } from "react";
import {
  MaterialReactTable,
  useMaterialReactTable,
} from "material-react-table";
import { Box, Button } from '@mui/material';
import { mkConfig, generateCsv, download } from 'export-to-csv';
import FileDownloadIcon from '@mui/icons-material/FileDownload';

const csvConfig = mkConfig({
  fieldSeparator: ',',
  decimalSeparator: '.',
  useKeysAsHeaders: true,
});

const handleExportRows = (rows) => {
  const rowData = rows.map((row) => row.original);
  const csv = generateCsv(csvConfig)(rowData);
  download(csvConfig)(csv);
};

const DisplayDataFrame = ({ data, schema }) => {
  const columns = useMemo(() => schema, [schema]);

  const memoizedData = useMemo(() => data, [data]);

  const table = useMaterialReactTable({
    columns,
    data: memoizedData, // Use the memoized data
    renderTopToolbarCustomActions: ({ table }) => (
      <Box
        sx={{
          display: 'flex',
          gap: '16px',
          padding: '8px',
          flexWrap: 'wrap',
        }}
      >
        <Button
          disabled={table.getPrePaginationRowModel().rows.length === 0}
          //export all rows, including from the next page, (still respects filtering and sorting)
          onClick={() =>
            handleExportRows(table.getPrePaginationRowModel().rows)
          }
          startIcon={<FileDownloadIcon />}
        >
          Export All Rows
        </Button>
        <Button
          disabled={table.getRowModel().rows.length === 0}
          //export all rows as seen on the screen (respects pagination, sorting, filtering, etc.)
          onClick={() => handleExportRows(table.getRowModel().rows)}
          startIcon={<FileDownloadIcon />}
        >
          Export Page Rows
        </Button>
      </Box>
    ),
  });

  return <MaterialReactTable table={table} />;
};

export default DisplayDataFrame;
