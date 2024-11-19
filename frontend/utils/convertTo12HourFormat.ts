export default function (time: string): string {
    const [hours, minutes] = time.split(":"); // Ignore seconds and milliseconds
    let hour = parseInt(hours, 10);
    const period = hour >= 12 ? "PM" : "AM";
    hour = hour % 12 || 12; // Convert 0 to 12 for midnight and adjust for PM

    return `${hour}:${minutes} ${period}`;
}