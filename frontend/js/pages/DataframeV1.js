import React, { useState } from 'react';
import api from '../store/api';

const DataframeV1 = () => {
    const [file, setFile] = useState(null);
    const [dataFrame, setDataFrame] = useState(null);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };


    const handleFileUpload = async () => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/api/rest/dataframes/', formData, {
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
        <div>
            <h2>Upload CSV or Excel File</h2>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleFileUpload}>Upload</button>

            {dataFrame && (
                <div>
                    <h2>DataFrame Display</h2>
                    <table>
                        <thead>
                            <tr>
                                {Object.keys(dataFrame).map((column, index) => (
                                    <th key={index}>{column}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {dataFrame[Object.keys(dataFrame)[0]].map((_, rowIndex) => (
                                <tr key={rowIndex}>
                                    {Object.keys(dataFrame).map((column) => (
                                        <td key={column}>{dataFrame[column][rowIndex]}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default DataframeV1;
