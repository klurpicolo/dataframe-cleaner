import { Download as DownloadIcon } from "@mui/icons-material";
import { Box, CircularProgress, IconButton } from "@mui/material";
import { MaterialReactTable } from "material-react-table";
import { useMemo, useState } from "react";

import api from "../store/api";

const DisplayDataFrameMetadata = ({ dataframeId, versionStatus }) => {
  const [downloadingVersion, setDownloadingVersion] = useState(null);

  const handleDownload = async (dataframe_id, version_id) => {
    try {
      setDownloadingVersion(version_id); // Set downloading version
      const response = await api.get(
        `/api/rest/dataframes/${dataframe_id}/download/${version_id}`,
        { responseType: "blob" },
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `processed_data_${version_id}.csv`);
      document.body.appendChild(link);
      link.click();
      setDownloadingVersion(null); // Reset downloading version
    } catch (error) {
      console.error("Error downloading file:", error);
      setDownloadingVersion(null); // Reset downloading version
    }
  };

  const columns = useMemo(
    () => [
      {
        accessorKey: "version_id",
        header: "Version",
        maxSize: 80,
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
          grow: false,
        },
      }}
      enableColumnActions={false}
      enableColumnFilters={false}
      enableColumnOrdering={false}
      enableRowActions
      enableSorting={false}
      initialState={{
        pagination: { pageSize: 3, pageIndex: 0 },
        showGlobalFilter: false,
        density: "compact",
      }}
      layoutMode="grid"
      muiPaginationProps={{
        rowsPerPageOptions: [3, 5],
        variant: "outlined",
      }}
      paginationDisplayMode="pages"
      renderRowActions={({ row }) => (
        <Box sx={{ display: "flex", flexWrap: "nowrap", gap: "8px" }}>
          {downloadingVersion === row.original.version_id ? (
            <CircularProgress color="primary" size={24} />
          ) : (
            <IconButton
              color="primary"
              onClick={() =>
                handleDownload(dataframeId, row.original.version_id)
              }
            >
              <DownloadIcon />
            </IconButton>
          )}
        </Box>
      )}
      rowsPerPageOptions={[5]}
    />
  );
};

export default DisplayDataFrameMetadata;
