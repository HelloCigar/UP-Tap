<template> 
    <div class="flex flex-col h-screen">
        <div class="flex flex-1 overflow-hidden">
            <div class="flex p-4">
                <Sidebar />
            </div>
            <UDivider orientation="vertical" />
            <div class="flex flex-1 flex-col h-full">
                <slot></slot>
            </div>
        </div>
    </div>     
</template>
