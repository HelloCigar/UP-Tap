<script setup lang="ts">
import { TimeTable, type TimeTableItem, type TimeTableLocation } from 'vue3-timetable';

const props = defineProps<{
  subjects: Subjects[]
}>()

function getItems() {
    if(!props) return

    const schedules: TimeTableItem[] = []

    const start = new Date()
    const end = new Date()

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
        console.log(i)
    })

    console.log(schedules)

    return schedules
}

let items = getItems()

watchEffect(() => {
  // runs only once before 3.5
  // re-runs when the "foo" prop changes in 3.5+
  console.log(props.subjects)
  items = getItems()
})

const locations: TimeTableLocation[] = [
    {
        id: "Sunday",
        name: "Sunday",
    },
    {
        id: "Monday",
        name:"Monday",
    },
    {
        id: "Tuesday",
        name:"Tuesday",
    },
    {
        id: "Wednesday",
        name:"Wednesday",
    },
    {
        id: "Thursday",
        name:"Thursday",
    },
    {
        id: "Friday",
        name:"Friday",
    },
    {
        id: "Saturday",
        name:"Saturday",
    },
    ];


</script>

<template>
    <div class="timetable">
        <TimeTable variant="vertical" :items="items" :locations="locations" />
    </div>
</template>
