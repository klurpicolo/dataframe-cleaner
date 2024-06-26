import {
  Box,
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
import Alert from "@mui/material/Alert";
import React, { useState, useEffect } from "react";

import DisplayDataFrame from "../component/DisplayDataFrame";
import DisplayDataFrameMetadata from "../component/DisplayDataFrameMetadata";
import api from "../store/api";

const OperationType = {
  ApplyScript: "apply_script",
  FillNull: "fill_null",
};

const DataframeCleanerPage = () => {
  const [file, setFile] = useState(null);
  const [dataFrameMeta, setDataFrameMeta] = useState([]);
  const [dataFrameId, setDataFrameId] = useState(null);
  const [dataFrame, setDataFrame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showApplyScriptForm, setShowApplyScriptForm] = useState(false);
  const [operationAndColumn, setOperationAndColumn] = useState(null);
  const [dialogInput, setDialogInput] = useState("");
  const [errorDialog, setErrorDialog] = useState(null);

  const fetchDataFrameVersion = async (dataframe_id) => {
    try {
      const response = await api.get(`/api/dataframes/${dataframe_id}/`);
      setDataFrameMeta(response.data);
      const noneVersionProcessing = !response.data.versions.some(
        (version) => version.status === "processing",
      );
      if (noneVersionProcessing) {
        setLoading(false);
        const lastVersion =
          response.data.versions[response.data.versions.length - 1];
        if (lastVersion.status === "failed") {
          setErrorDialog(
            `failed to process operation ${lastVersion.operation} with script ${lastVersion.script} on column ${lastVersion.column}`,
          );
        } else {
          const { version_id } = lastVersion;
          await fetchDataFrame(dataframe_id, version_id);
        }
      }
    } catch (error) {
      console.error("Error processing DataFrame:", error);
    }
  };

  const fetchDataFrame = async (dataframe_id, version_id) => {
    console.log("fetchDataFrame", fetchDataFrame);
    try {
      const response = await api.get(
        `/api/dataframes/${dataframe_id}/versions/${version_id}`,
      );
      console.log("fetchDataFrame response", response);
      setDataFrame(response.data);
    } catch (error) {
      console.error("Error fetching data with parameters:", error);
    }
  };

  useEffect(() => {
    let interval;
    if (loading && dataFrameId !== null) {
      interval = setInterval(() => {
        fetchDataFrameVersion(dataFrameId);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [loading, dataFrameId]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      setLoading(true);
      setDataFrameId(null);
      const startTime = new Date();
      const response = await api.post("/api/dataframes-async/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      const endTime = new Date();
      const timeDiffInSeconds = (endTime - startTime) / 1000;
      console.log("API call took", timeDiffInSeconds, "seconds to complete");
      console.log("response is", response.data);
      setDataFrameId(response.data.dataframe_id);
    } catch (error) {
      console.error("Error uploading file:", error);
      setLoading(false);
      setErrorDialog(
        `Error code ${error.response.status} with message ${error.response.data.message}`,
      );
    }
  };

  const handleProcessColumnAction = async (
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
    try {
      setLoading(true);
      const response = await api.post(
        `/api/dataframes/${dataFrame.dataframe_id}/process-async/`,
        requestBody,
      );
      fetchDataFrameVersion(dataFrameId);
    } catch (error) {
      console.error("Error processing DataFrame:", error);
    }
  };

  const handleProcessAction = () => {
    handleProcessColumnAction(
      operationAndColumn.field,
      operationAndColumn.operation_type,
      operationAndColumn.operation_type === OperationType.ApplyScript
        ? dialogInput
        : null,
      operationAndColumn.operation_type === OperationType.FillNull
        ? dialogInput
        : null,
    );
    setDialogInput("");
    setShowApplyScriptForm(false);
  };

  function mapToType(field) {
    if (field.type === "string") {
      return "text";
    }
    if (field.type === "datetime") {
      return "date";
    }
    if (field?.constraints?.enum !== undefined) {
      return "category";
    }
    return field.type;
  }

  return (
    <>
      <div style={{ display: "flex" }}>
        <div style={{ marginRight: "20px" }}>
          <h1>Dataframe Cleaner</h1>
          <h3>Upload CSV or Excel File</h3>
          <input type="file" onChange={handleFileChange} />
          <button
            disabled={file === null}
            type="submit"
            onClick={handleFileUpload}
          >
            Upload
          </button>
          {loading && <CircularProgress size={24} />}
        </div>
        <div style={{ width: "100%" }}>
          <DisplayDataFrameMetadata
            dataframeId={dataFrameMeta.dataframe_id}
            versionStatus={dataFrameMeta?.versions ?? []}
          />
        </div>
      </div>

      {errorDialog && (
        <Alert
          severity="warning"
          onClose={() => {
            setErrorDialog(null);
          }}
        >
          {errorDialog}
        </Alert>
      )}

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
          {operationAndColumn?.operation_type === OperationType.ApplyScript
            ? "Apply script to "
            : "Fill null value with "}
          {operationAndColumn?.field}
        </DialogTitle>

        <DialogContent>
          <TextField
            fullWidth
            helperText={
              operationAndColumn?.operation_type === OperationType.ApplyScript
                ? "Input the Python function in Lambda format with 'x' as input, for example x+2"
                : "Input the value to fill null value with, it should have the same type as the column"
            }
            label={
              operationAndColumn?.operation_type === OperationType.ApplyScript
                ? "Python Code"
                : "Value to fill"
            }
            multiline
            rows={10}
            value={dialogInput}
            variant="filled"
            onChange={(e) => setDialogInput(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowApplyScriptForm(false)}>Cancel</Button>
          <Button disabled={dialogInput === ""} onClick={handleProcessAction}>
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      {dataFrame && (
        <>
          {dataFrame.actual_size !== dataFrame.limit_size && (
            <Alert severity="warning">
              The table is not display the whole data ({dataFrame.actual_size}{" "}
              rows) because it reach maximum display size (
              {dataFrame.limit_size} rows). To get the all processed data,
              please download as csv.
            </Alert>
          )}
          <DisplayDataFrame
            data={dataFrame.data.data}
            schema={dataFrame.data.schema.fields.map((field) => ({
              accessorKey: field.name, // TODO fix issue with column contain .
              header: `${field.name}[${mapToType(field)}]`, // TODO find the better way to display data type
              Cell: (
                { renderedCellValue }, // To support renderring boolean type
              ) => (
                <Box>
                  {typeof renderedCellValue === "boolean" ? (
                    <span>{renderedCellValue ? "true" : "false"}</span>
                  ) : (
                    <span>{renderedCellValue}</span>
                  )}
                </Box>
              ),
              renderColumnActionsMenuItems: ({
                closeMenu,
                internalColumnMenuItems,
              }) => [
                <MenuItem
                  key="cast_to_numeric"
                  onClick={() => {
                    handleProcessColumnAction(field.name, "cast_to_numeric");
                    closeMenu();
                  }}
                >
                  Cast to Numeric
                </MenuItem>,
                <MenuItem
                  key="cast_to_string"
                  onClick={() => {
                    handleProcessColumnAction(field.name, "cast_to_string");
                    closeMenu();
                  }}
                >
                  Cast to String
                </MenuItem>,
                <MenuItem
                  key="cast_to_datetime"
                  onClick={() => {
                    handleProcessColumnAction(field.name, "cast_to_datetime");
                    closeMenu();
                  }}
                >
                  Cast to Datetime
                </MenuItem>,
                <MenuItem
                  key="cast_to_timedelta"
                  onClick={() => {
                    handleProcessColumnAction(field.name, "cast_to_timedelta");
                    closeMenu();
                  }}
                >
                  Cast to Timedelta
                </MenuItem>,
                <MenuItem
                  key="cast_to_boolean"
                  onClick={() => {
                    handleProcessColumnAction(field.name, "cast_to_boolean");
                    closeMenu();
                  }}
                >
                  Cast to Boolean
                </MenuItem>,
                <MenuItem
                  key="cast_to_category"
                  onClick={() => {
                    handleProcessColumnAction(field.name, "cast_to_category");
                    closeMenu();
                  }}
                >
                  Cast to Category
                </MenuItem>,
                <MenuItem
                  key="apply_script"
                  onClick={() => {
                    setShowApplyScriptForm(true);
                    setOperationAndColumn({
                      operation_type: OperationType.ApplyScript,
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
                      operation_type: OperationType.FillNull,
                      field: field.name,
                    });
                    closeMenu();
                  }}
                >
                  Fill null value
                </MenuItem>,
                <Divider key="divider-1" />,
                ...internalColumnMenuItems,
              ],
              size: 150,
            }))}
          />
        </>
      )}
    </>
  );
};

export default DataframeCleanerPage;
