import React, { useEffect, useMemo, useState } from 'react';
import DisplayDataFrame from '../component/DisplayDataFrame'
import api from '../store/api';

const data = [
  {
    name: {
      firstName: 'Klur2',
      lastName: 'Doe',
    },
    address: '261 Erdman Ford',
    city: 'East Daphne',
    state: 'Kentucky',
  },
  {
    name: {
      firstName: 'Jane',
      lastName: 'Doe',
    },
    address: '769 Dominic Grove',
    city: 'Columbus',
    state: 'Ohio',
  },
  {
    name: {
      firstName: 'Joe',
      lastName: 'Doe',
    },
    address: '566 Brakus Inlet',
    city: 'South Linda',
    state: 'West Virginia',
  },
  {
    name: {
      firstName: 'Kevin',
      lastName: 'Vandy',
    },
    address: '722 Emie Stream',
    city: 'Lincoln',
    state: 'Nebraska',
  },
  {
    name: {
      firstName: 'Joshua',
      lastName: 'Rolluffs',
    },
    address: '32188 Larkin Turnpike',
    city: 'Charleston',
    state: 'South Carolina',
  },
];

const schema = [
  {
    accessorKey: 'name.firstName', //access nested data with dot notation
    header: 'First Name klur2',
    size: 150,
  },
  {
    accessorKey: 'name.lastName',
    header: 'Last Name',
    size: 150,
  },
  {
    accessorKey: 'address', //normal accessorKey
    header: 'Address',
    size: 200,
  },
  {
    accessorKey: 'city',
    header: 'City',
    size: 150,
  },
  {
    accessorKey: 'state',
    header: 'State',
    size: 150,
  },
]

const DataframeV2 = () => {
  const [file, setFile] = useState(null);
  const [dataFrame, setDataFrame] = useState(null);

  const handleFileChange = (event) => {
      setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
      const formData = new FormData();
      formData.append('file', file);

      try {
          const response = await api.post('/api/rest/dataframesv2/', formData, {
              headers: {
                  'Content-Type': 'multipart/form-data'
              }
          });
          setDataFrame(response.data);
      } catch (error) {
          console.error('Error uploading file:', error);
      }
  };

  return (
    <>
      <h1>Dataframe V2</h1>
      <h2>Upload CSV or Excel File</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload</button>
      {/* <DisplayDataFrame data={data} schema={schema}></DisplayDataFrame> */}
      {dataFrame && (
        <DisplayDataFrame
          data={dataFrame.data.data} // Use data from the API response
          schema={dataFrame.data.schema.fields.map(field => ({
            accessorKey: field.name, // TODO fix issue with column contain .
            header: field.name,
            size: 150
          }))} // Convert schema fields to match the expected format
        />
      )}
    </>
  )
}


export default DataframeV2
