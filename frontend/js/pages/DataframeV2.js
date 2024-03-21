import React, { useState } from "react";
import { Divider, MenuItem, CircularProgress } from "@mui/material";
import DisplayDataFrame from "../component/DisplayDataFrame";
import api from "../store/api";

const DataframeV2 = () => {
  const [file, setFile] = useState(null);
  const [dataFrame, setDataFrame] = useState(null);
  const [loading, setLoading] = useState(false); // Add loading state

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      setLoading(true); // Set loading state to true when uploading file
      const response = await api.post("/api/rest/dataframes/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setLoading(false); // Set loading state to false when response is received
      setDataFrame(response.data);
    } catch (error) {
      console.error("Error uploading file:", error);
      setLoading(false); // Set loading state to false when response is received
    }
  };

  const handleColumnAction = async (operationType, column) => {
    const requestBody = {
      version_id: dataFrame.version_id,
      column: column,
      operation: {
        type: operationType,
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
      // setDataFrame({ ...dataFrame, data: response.data.data });
      setDataFrame(response.data);
    } catch (error) {
      console.error("Error processing DataFrame:", error);
    }
  };

  function mapToType(field) {
    console.log(field?.constraints?.enum?.length);
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
      {dataFrame && (
        <>
          <p>dataframe id: {dataFrame.dataframe_id}</p>
          <p>previous version id: {dataFrame.previous_version_id}</p>
          <p>version id: {dataFrame.version_id}</p>
          <DisplayDataFrame
            data={dataFrame.data.data}
            schema={dataFrame.data.schema.fields.map((field) => ({
              accessorKey: field.name, // TODO fix issue with column contain .
              header: field.name + "[" + mapToType(field) + "]", //TODO find the better way to display data
              renderColumnActionsMenuItems: ({
                closeMenu,
                internalColumnMenuItems,
              }) => [
                ...internalColumnMenuItems,
                <Divider key="divider-1" />,
                <MenuItem
                  key={"cast_to_numeric"}
                  onClick={() => {
                    handleColumnAction("cast_to_numeric", field.name);
                    closeMenu();
                  }}
                >
                  Cast to Numeric
                </MenuItem>,
                <MenuItem
                  key={"cast_to_string"}
                  onClick={() => {
                    handleColumnAction("cast_to_string", field.name);
                    closeMenu();
                  }}
                >
                  Cast to String
                </MenuItem>,
                <MenuItem
                  key={"cast_to_datetime"}
                  onClick={() => {
                    handleColumnAction("cast_to_datetime", field.name);
                    closeMenu();
                  }}
                >
                  Cast to Datetime
                </MenuItem>,
                <MenuItem
                  key={"cast_to_boolean"}
                  onClick={() => {
                    handleColumnAction("cast_to_boolean", field.name);
                    closeMenu();
                  }}
                >
                  Cast to Boolean
                </MenuItem>,
              ],
              size: 150,
            }))} // Convert schema fields to match the expected format
          />
        </>
      )}
    </>
  );
};

export default DataframeV2;
