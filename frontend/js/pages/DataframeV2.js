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
import React, { useState } from "react";

import DisplayDataFrame from "../component/DisplayDataFrame";
import api from "../store/api";

const DataframeV2 = () => {
  const [file, setFile] = useState(null);
  const [dataFrame, setDataFrame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showApplyScriptForm, setShowApplyScriptForm] = useState(false);
  const [operationAndColumn, setOperationAndColumn] = useState(null);
  const [dialogInput, setDialogInput] = useState("");

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

  const handleColumnAction = async (
    column,
    operationType,
    script = null,
    to_fill = null,
  ) => {
    const requestBody = {
      version_id: dataFrame.version_id,
      column,
      operation: {
        type: operationType,
        script,
        to_fill,
      },
    };
    console.log(
      `the request body is${JSON.stringify(requestBody, undefined, 4)}`,
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
    console.log(`handleApplyScript${dialogInput} to ${operationAndColumn}`);
    handleColumnAction(
      operationAndColumn.field,
      operationAndColumn.operation_type,
      operationAndColumn.operation_type === "apply_script" ? dialogInput : null,
      operationAndColumn.operation_type === "fill_null" ? dialogInput : null,
    );
    setDialogInput("");
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
        fullWidth
        maxWidth="lg"
        open={showApplyScriptForm}
        onClose={() => {
          setDialogInput("");
          setShowApplyScriptForm(false);
        }}
      >
        <DialogTitle>
          {operationAndColumn?.operation_type === "apply_script"
            ? "Apply script to "
            : "Fill null value with "}
          {operationAndColumn?.field}
        </DialogTitle>

        <DialogContent>
          <TextField
            fullWidth
            helperText={
              operationAndColumn?.operation_type === "apply_script"
                ? "Input the Python function in Lambda format with 'x' as input, for example x+2"
                : "Input the value to fill null value with, it should have the same type as the column"
            }
            label="Python Code"
            multiline
            rows={10}
            value={dialogInput}
            variant="filled"
            onChange={(e) => setDialogInput(e.target.value)}
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
              header: `${field.name}[${mapToType(field)}]`, // TODO find the better way to display data type
              renderColumnActionsMenuItems: ({
                closeMenu,
                internalColumnMenuItems,
              }) => [
                ...internalColumnMenuItems,
                <Divider key="divider-1" />,
                <MenuItem
                  key="cast_to_numeric"
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_numeric");
                    closeMenu();
                  }}
                >
                  Cast to Numeric
                </MenuItem>,
                <MenuItem
                  key="cast_to_string"
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_string");
                    closeMenu();
                  }}
                >
                  Cast to String
                </MenuItem>,
                <MenuItem
                  key="cast_to_datetime"
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_datetime");
                    closeMenu();
                  }}
                >
                  Cast to Datetime
                </MenuItem>,
                <MenuItem
                  key="cast_to_boolean"
                  onClick={() => {
                    handleColumnAction(field.name, "cast_to_boolean");
                    closeMenu();
                  }}
                >
                  Cast to Boolean
                </MenuItem>,
                <MenuItem
                  key="apply_script"
                  onClick={() => {
                    setShowApplyScriptForm(true);
                    setOperationAndColumn({
                      operation_type: "apply_script",
                      field: field.name,
                    });
                    closeMenu();
                  }}
                >
                  Apply function
                </MenuItem>,
                <MenuItem
                  key="fill_null"
                  onClick={() => {
                    setShowApplyScriptForm(true);
                    setOperationAndColumn({
                      operation_type: "fill_null",
                      field: field.name,
                    });
                    closeMenu();
                  }}
                >
                  Fill null value
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
