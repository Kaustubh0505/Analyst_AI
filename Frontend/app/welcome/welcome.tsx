import { useState } from "react";
import axios from "axios";

export function Welcome() {
  const [query, setQuery] = useState<string>("");
  const [response, setResponse] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Handle file input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  // Send data to backend
  const handleSubmit = async () => {
    try {
      setLoading(true);

      const url = import.meta.env.VITE_BACKEND_URL;

      const formData = new FormData();
      formData.append("query", query);

      if (file) {
        formData.append("file", file);
      }

      const res = await axios.post(`${url}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResponse(res.data.response);
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="bg-white shadow-xl text-black rounded-2xl p-6 w-full max-w-lg space-y-5">

        {/* Title */}
        <h1 className="text-2xl font-bold text-center">
          AI Query Tool 🚀
        </h1>

        {/* Query Input */}
        <input
          type="text"
          placeholder="Type your query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full border p-3 rounded-lg outline-none focus:ring-2 text-black focus:ring-blue-400"
        />

        {/* File Upload */}
        <div className="flex flex-col gap-2">
          <label className="text-sm text-black font-medium">Upload CSV (optional)</label>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="w-full"
          />
          {file && (
            <p className="text-sm text-gray-600">
              Selected: {file.name}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          className="w-full text-black  bg-blue-500  py-2 rounded-lg hover:bg-blue-600 transition"
        >
          {loading ? "Processing..." : "Submit"}
        </button>

        {/* Response Section */}
        {response && (
          <div className="bg-gray-50 p-4 rounded-lg border">
            <h2 className="font-semibold mb-2">Response:</h2>
            <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}