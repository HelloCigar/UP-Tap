import Papa from 'papaparse';

export interface CsvValidationResult {
  valid: boolean;
  missingFields: string[];
  parsedFields: string[];
}

/**
 * Reads only the header row of a CSV File and checks
 * whether all requiredFields are present.
 *
 * @param csvFile         The CSV file chosen by the user.
 * @param requiredFields  Array of field names that must appear in the header.
 * @param options         Optional PapaParse config (delimiter, newline, etc).
 * @returns Promise resolving to validation result.
 */
export function validateCsvFields(
  csvFile: File,
  requiredFields: string[],
  options?: {
    delimiter?: string;
    newline?: '\r' | '\n' | '\r\n';
    encoding?: string;
  }
): Promise<CsvValidationResult> {
  return new Promise((resolve, reject) => {
    Papa.parse<string[]>(csvFile, {
      ...options,
      preview: 1,             // only parse first row
      header: false,          // we want raw array of fields
      dynamicTyping: false,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.errors.length > 0) {
          return reject(
            new Error(
              `CSV parse error: ${results.errors
                .map((e) => e.message)
                .join('; ')}`
            )
          );
        }

        const parsedFields = results.data[0] || [];
        const missingFields = requiredFields.filter(
          (f) => !parsedFields.includes(f)
        );

        resolve({
          valid: missingFields.length === 0,
          missingFields,
          parsedFields,
        });
      },
      error: (err) => {
        reject(err);
      },
    });
  });
}
