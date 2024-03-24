import { Download as DownloadIcon } from "@mui/icons-material";
import { Box, CircularProgress, IconButton } from "@mui/material";
import { MaterialReactTable } from "material-react-table";
import { useMemo, useState } from "react";

import api from "../store/api";

const DisplayDataFrameMetadata = ({ dataframeId, versionStatus }) => {
  const [downloadingVersion, setDownloadingVersion] = useState(null); // State to track downloading version

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
    />
  );
};

export default DisplayDataFrameMetadata;
