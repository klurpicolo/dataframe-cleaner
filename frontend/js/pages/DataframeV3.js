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

import DisplayDataFrameMetadata from "../component/DisplayDataFrameMetadata";
import DisplayDataFrameV3 from "../component/DisplayDataFrameV3";
import api from "../store/api";

const DataframeV3 = () => {
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
    console.log("callfetchDataFrameVersion");
    try {
      const response = await api.get(`/api/rest/dataframes/${dataframe_id}/`);
      setDataFrameMeta(response.data);
      const allVersionsProcessed = response.data.versions.every(
        (version) => version.status === "processed",
      );
      if (allVersionsProcessed) {
        setLoading(false);
        const lastVersion =
          response.data.versions[response.data.versions.length - 1];
        const { version_id } = lastVersion;
        await fetchDataFrame(dataframe_id, version_id);
      }
    } catch (error) {
      console.error("Error processing DataFrame:", error);
    }
  };

  const fetchDataFrame = async (dataframe_id, version_id) => {
    console.log("fetchDataFrame", fetchDataFrame);
    try {
      const response = await api.get(
        `/api/rest/dataframes/${dataframe_id}/versions/${version_id}`,
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
      }, 1000); // 1000 milliseconds = 1 second
    }

    // Cleanup function to clear interval when component unmounts
    return () => clearInterval(interval);
  }, [loading, dataFrameId]); // Empty dependency array to run effect only once on mount

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
      const response = await api.post("/api/rest/dataframes-async/", formData, {
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
      setLoading(true);
      const response = await api.post(
        `/api/rest/dataframes/${dataFrame.dataframe_id}/process-async/`,
        requestBody,
      );
      fetchDataFrameVersion(dataFrameId);
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
      <div style={{ display: "flex" }}>
        <div style={{ marginRight: "20px" }}>
          <h1>Dataframe Cleaner</h1>
          <h3>Upload CSV or Excel File</h3>
          <input type="file" onChange={handleFileChange} />
          <button type="submit" onClick={handleFileUpload}>
            Upload
          </button>
          {loading && <CircularProgress />}
        </div>
        <div style={{ width: "100%" }}>
          <DisplayDataFrameMetadata
            dataframeId={dataFrameMeta.dataframe_id}
            versionStatus={dataFrameMeta?.versions ?? []}
          />
        </div>
      </div>

      {errorDialog && (
        <>
          <Alert
            severity="warning"
            onClose={() => {
              setErrorDialog(null);
            }}
          >
            {errorDialog}
          </Alert>
          {/* <Alert
            action={
              <Button color="inherit" size="small">
                UNDO
              </Button>
            }
            severity="success"
          >
            This Alert uses a Button component for its action.
          </Alert> */}
        </>
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
          {dataFrame.actual_size !== dataFrame.limit_size && (
            <Alert severity="warning">
              The table is not display the whole data ({dataFrame.actual_size}{" "}
              rows) because it reach maximum display size (
              {dataFrame.limit_size} rows). To get the all processed data,
              please download as csv.
            </Alert>
          )}
          <DisplayDataFrameV3
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

export default DataframeV3;
