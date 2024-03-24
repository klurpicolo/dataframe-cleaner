import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Email as EmailIcon,
} from "@mui/icons-material";
import { Box, IconButton } from "@mui/material";
import { MaterialReactTable } from "material-react-table";
import { useMemo } from "react";

const DisplayDataFrameMetadata = ({ versionStatus }) => {
  const columns = useMemo(
    () => [
      {
        accessorKey: "version_id",
        header: "Version",
        size: 50,
      },
      {
        accessorKey: "operation",
        header: "Operation type",
        size: 50,
      },
      {
        accessorKey: "status",
        header: "Processing status",
        size: 30,
      },
    ],
    [],
  );

  const memoizedData = useMemo(() => versionStatus, [versionStatus]);
  return (
    <MaterialReactTable
      columns={columns}
      data={memoizedData}
      displayColumnDefOptions={{
        "mrt-row-actions": {
          size: 180, // if using layoutMode that is not 'semantic', the columns will not auto-size, so you need to set the size manually
          grow: false,
        },
      }}
      enableRowActions
      layoutMode="grid"
      renderRowActions={({ row, table }) => (
        <Box sx={{ display: "flex", flexWrap: "nowrap", gap: "8px" }}>
          <IconButton
            color="primary"
            onClick={() =>
              window.open(
                `mailto:kevinvandy@mailinator.com?subject=Hello ${row.original.firstName}!`,
              )
            }
          >
            <EmailIcon />
          </IconButton>
          <IconButton
            color="secondary"
            onClick={() => {
              table.setEditingRow(row);
            }}
          >
            <EditIcon />
          </IconButton>
          <IconButton
            color="error"
            onClick={() => {
              data.splice(row.index, 1); // assuming simple data table
              setData([...data]);
            }}
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      )}
    />
  );
};

export default DisplayDataFrameMetadata;
