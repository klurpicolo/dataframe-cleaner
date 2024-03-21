import React, { useState } from "react";
import {
  Button,
  Dialog,
  Divider,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  TextField,
  CircularProgress,
} from "@mui/material";
import DisplayDataFrame from "../component/DisplayDataFrame";
import api from "../store/api";

const DataframeV2 = () => {
  const [file, setFile] = useState(null);
  const [dataFrame, setDataFrame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showApplyScriptForm, setShowApplyScriptForm] = useState(false);
  const [applingScriptColumn, setApplingScriptColumn] = useState(null);
  const [pythonCode, setPythonCode] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      setLoading(true);
      const startTime = new Date();
      const response = await api.post("/api/rest/dataframes/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      const endTime = new Date();
      const timeDiffInSeconds = (endTime - startTime) / 1000; // Convert milliseconds to seconds
      console.log("API call took", timeDiffInSeconds, "seconds to complete");
      setLoading(false);
      setDataFrame(response.data);
    } catch (error) {
      console.error("Error uploading file:", error);
      setLoading(false);
    }
  };

  const handleColumnAction = async (column, operationType, script = null) => {
    const requestBody = {
      version_id: dataFrame.version_id,
      column: column,
      operation: {
        type: operationType,
        script: script,
      },
    };
    console.log(
      "the request body is" + JSON.stringify(requestBody, undefined, 4),
    );

    try {
      const response = await api.post(
        `/api/rest/dataframes/${dataFrame.dataframe_id}/process/`,
        requestBody,
      );
      setDataFrame(response.data);
    } catch (error) {
      console.error("Error processing DataFrame:", error);
    }
  };

  const handleApplyScript = () => {
    console.log(
      "handleApplyScript" + pythonCode + " to " + applingScriptColumn,
    );
    handleColumnAction(applingScriptColumn, "apply_script", pythonCode);
    setPythonCode("");
    setShowApplyScriptForm(false);
  };

  function mapToType(field) {
    if (field?.constraints?.enum !== undefined) {
      return "category";
    }
    return field.type;
  }

  return (
    <>
      <h1>Dataframe V2</h1>
      <h2>Upload CSV or Excel File</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload</button>
      {loading && <CircularProgress />}

      <Dialog
        open={showApplyScriptForm}
        onClose={() => setShowApplyScriptForm(false)}
        fullWidth
        maxWidth="lg"
      >
        <DialogTitle>Apply script {applingScriptColumn}</DialogTitle>
        <DialogContent>
          <TextField
            label="Python Code"
            multiline
            rows={10}
            variant="outlined"
            fullWidth
            value={pythonCode}
            onChange={(e) => setPythonCode(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowApplyScriptForm(false)}>Cancel</Button>
          <Button onClick={handleApplyScript}>Submit</Button>
        </DialogActions>
      </Dialog>

      {dataFrame && (
        <>
          <p>dataframe id: {dataFrame.dataframe_id}</p>
          <p>previous version id: {dataFrame.previous_version_id}</p>
          <p>version id: {dataFrame.version_id}</p>
          <DisplayDataFrame
            data={dataFrame.data.data}
            schema={dataFrame.data.schema.fields.map((field) => ({
              accessorKey: field.name, // TODO fix issue with column contain .
              header: field.name + "[" + mapToType(field) + "]", //TODO find the better way to display data type
              renderColumnActionsMenuItems: ({
                closeMenu,
                internalColumnMenuItems,
              }) => [
                ...internalColumnMenuItems,
                <Divider key="divider-1" />,
                <MenuItem
                  key={"cast_to_numeric"}
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_numeric");
                    closeMenu();
                  }}
                >
                  Cast to Numeric
                </MenuItem>,
                <MenuItem
                  key={"cast_to_string"}
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_string");
                    closeMenu();
                  }}
                >
                  Cast to String
                </MenuItem>,
                <MenuItem
                  key={"cast_to_datetime"}
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_datetime");
                    closeMenu();
                  }}
                >
                  Cast to Datetime
                </MenuItem>,
                <MenuItem
                  key={"cast_to_boolean"}
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_boolean");
                    closeMenu();
                  }}
                >
                  Cast to Boolean
                </MenuItem>,
                <MenuItem
                  key={"apply_function"}
                  onClick={() => {
                    setShowApplyScriptForm(true);
                    setApplingScriptColumn(field.name);
                    closeMenu();
                  }}
                >
                  Apply function
                </MenuItem>,
              ],
              size: 150,
            }))}
          />
        </>
      )}
    </>
  );
};

export default DataframeV2;
