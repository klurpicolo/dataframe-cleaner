import { render, fireEvent, waitFor } from "@testing-library/react";
import React from "react";

import api from "../../store/api";
import DataframeCleanerPage from "../DataframeCleanerPage";

// Mocking api module
jest.mock("../../store/api", () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

describe("DataframeCleanerPage", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test("renders without crashing", () => {
    render(<DataframeCleanerPage />);
  });

  test("makes API call on file upload", async () => {
    api.post.mockResolvedValueOnce({ data: { dataframe_id: 123 } });
    const { getByText } = render(<DataframeCleanerPage />);
    const fileInput = getByText("Upload");
    fireEvent.click(fileInput);
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith(
      "/api/dataframes-async/",
      expect.any(FormData),
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
  });
});
