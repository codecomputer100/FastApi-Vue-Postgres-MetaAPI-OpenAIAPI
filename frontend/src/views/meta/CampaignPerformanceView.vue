<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Performance de Campaña</h1>
    <div v-if="loading">Cargando métricas...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else-if="performance" class="grid grid-cols-2 gap-4">
      <div class="p-4 bg-white shadow rounded">
        <h2 class="font-semibold text-lg">{{ performance.campaign_name }}</h2>
        <p><strong>Impresiones:</strong> {{ performance.impressions }}</p>
        <p><strong>Clics:</strong> {{ performance.clicks }}</p>
        <p><strong>CTR:</strong> {{ performance.ctr }}%</p>
        <p><strong>CPC:</strong> ${{ performance.cpc }}</p>
        <p><strong>CPM:</strong> ${{ performance.cpm }}</p>
        <p><strong>Gasto:</strong> ${{ performance.spend }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import apiClient from "@/service/api";
import { useRoute } from "vue-router";

const route = useRoute();
const performance = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    const id = route.params.id; // /performance/:id
    const { data } = await apiClient.get(`/meta/performance/${id}`);
    performance.value = data.performance;
  } catch (err) {
    error.value = err?.response?.data?.detail || "Error al obtener métricas";
  } finally {
    loading.value = false;
  }
});
</script>
