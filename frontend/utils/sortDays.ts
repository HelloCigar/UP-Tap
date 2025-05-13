export default function (days: DayData[]): DayData[] {
    const dayOrder = {
      Monday: 1,
      Tuesday: 2,
      Wednesday: 3,
      Thursday: 4,
      Friday: 5,
      Saturday: 6,
      Sunday: 7,
    }
  
    return [...days].sort((a, b) => {
      return dayOrder[a.day_of_week as keyof typeof dayOrder] - dayOrder[b.day_of_week as keyof typeof dayOrder]
    })
  }