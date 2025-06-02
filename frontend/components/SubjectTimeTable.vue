<script setup lang="ts">
import { TimeTable, type TimeTableItem, type TimeTableLocation } from 'vue3-timetable';

const props = defineProps<{
  subjects: SubjectOut[]
}>()

function getItems() {
    if(!props) return

    const schedules: TimeTableItem[] = []

    let i = 0
    props.subjects.forEach(sub => {
        let j = 0
        const date = new Date();
        const year  = date.getFullYear();
        let   month = date.getMonth() + 1;           // months are 0‑indexed
        let   day   = date.getDate();

        const strMonth = String(month).padStart(2, '0');      // ensure two digits
        const strDay   = String(day).padStart(2, '0');

        sub.schedule.forEach(sched => {
            
            schedules?.push(
                {
                    id: `e${(2*i) + j}`,
                    locationId: sched,
                    startDate: `${year}-${strMonth}-${strDay}T${sub.start_time}:00`,
                    endDate: `${year}-${strMonth}-${strDay}T${sub.end_time}:00`,
                    name: sub.subject_name,
                }
            )
            j+=1
        })
        i++
    })

    return schedules
}

let items = getItems()

watchEffect(() => {
  // runs only once before 3.5
  // re-runs when the "foo" prop changes in 3.5+
  console.log(props.subjects)
  items = getItems()
})

const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const todayIndex = new Date().getDay(); // 0 (Sun) to 6 (Sat)

const locations: TimeTableLocation[] = [
    {
        id: "Sunday",
        name: "Sunday",
        style: {
            backgroundColor: '#ef9a9a'
        }
    },
    {
        id: "Monday",
        name:"Monday",
        style: {
            backgroundColor: '#ef9a9a'
        }
    },
    {
        id: "Tuesday",
        name:"Tuesday",
        style: {
            backgroundColor: '#ef9a9a'
        }
    },
    {
        id: "Wednesday",
        name:"Wednesday",
        style: {
            backgroundColor: '#ef9a9a'
        }
    },
    {
        id: "Thursday",
        name:"Thursday",
        style: {
            backgroundColor: '#ef9a9a'
        }
    },
    {
        id: "Friday",
        name:"Friday",
        style: {
            backgroundColor: '#ef9a9a'
        }
    },
    {
        id: "Saturday",
        name:"Saturday",
        style: {
            backgroundColor: '#ef9a9a'
        },
    },
];

// Rotate the locations array to start from today
const rotatedLocations = [...locations.slice(todayIndex), ...locations.slice(0, todayIndex)];

const styles = {
    backgroundColor: '#fffff',
    dateBackgroundColor: '#ffffff',
    textColor: '#000000',
    itemBackgroundColor: '#f44336',
    itemTextColor: '#ffffff',
    locationBackgroundColor: '#f44336', 
    borderStyle: 'solid 1px #374151',
    timeMarkerColor: '#f44336',
}
</script>

<template>
    <div class="timetable">
        <TimeTable variant="vertical" :items="items" :locations="rotatedLocations" :styles="styles"/>
    </div>
</template>
