<template>
  <div class="card">
    <h3 class="mb-3">Campañas de Facebook</h3>

    <Button
      label="Actualizar"
      icon="pi pi-refresh"
      class="mb-3"
      @click="fetchCampaigns"
    />

    <DataTable :value="campaigns" paginator rows="5" responsiveLayout="scroll">
      <Column field="id" header="ID"></Column>
      <Column field="name" header="Nombre"></Column>
      <Column field="status" header="Estado"></Column>
      <Column field="objective" header="Objetivo"></Column>

      <!-- 🔥 Nueva columna con botón -->
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            label="Ver performance"
            icon="pi pi-chart-line"
            class="p-button-sm p-button-success"
            @click="goToPerformance(slotProps.data.id)"
          />
        </template>
      </Column>
    </DataTable>

    <p v-if="campaigns.length === 0 && loaded" class="mt-4 text-gray-500">
      No se encontraron campañas asociadas a tu cuenta.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/service/api';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const campaigns = ref([]);
const loaded = ref(false);
const router = useRouter(); // 👈 Necesario para navegar

async function fetchCampaigns() {
  try {
    const { data } = await apiClient.get('/meta/campaigns');
    campaigns.value = data.campaigns || [];
    loaded.value = true;
    console.log('Campañas:', campaigns.value);
  } catch (err) {
    console.error('Error campañas:', err?.response?.data || err.message);
  }
}

// 👇 Nueva función para ir al detalle de performance
function goToPerformance(id) {
  router.push(`/meta/performance/${id}`);
}

onMounted(fetchCampaigns);
</script>
