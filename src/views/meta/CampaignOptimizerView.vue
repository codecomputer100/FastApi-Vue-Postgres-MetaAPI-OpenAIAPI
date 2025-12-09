<template>
  <div class="card p-4">
    <h2 class="mb-4">Optimización de Campañas con IA</h2>

    <!-- 🧠 FORMULARIO DE PREGUNTAS -->
    <div v-if="!recommendation">
      <h3>Cuéntanos sobre tu campaña</h3>
      <div class="p-fluid formgrid grid">
        <div class="field col-12 md:col-6">
          <label>Rubro del negocio</label>
          <InputText v-model="form.business_type" placeholder="Ej. Belleza, educación, tecnología..." />
        </div>
        <div class="field col-12 md:col-6">
          <label>Objetivo de la campaña</label>
          <Dropdown v-model="form.objective" :options="objectives" placeholder="Selecciona un objetivo" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Presupuesto estimado (USD)</label>
          <InputNumber v-model="form.budget" mode="currency" currency="USD" locale="en-US" />
        </div>
      </div>

      <Button label="Generar recomendación IA" icon="pi pi-brain" class="mt-3 p-button-success" @click="generateRecommendation" />
    </div>

    <!-- 🧩 FORMULARIO AUTOLLENADO CON RESPUESTA DE LA IA -->
    <div v-else>
      <h3 class="mt-5">Configuración recomendada (editable)</h3>

      <!-- 🧱 CAMPAGNA -->
      <h4>🧱 Campaña</h4>
      <div class="p-fluid formgrid grid">
        <div class="field col-12 md:col-6">
          <label>Nombre</label>
          <InputText v-model="recommendation.campaign_name" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Objetivo</label>
          <InputText v-model="recommendation.objective" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Presupuesto recomendado (USD)</label>
          <InputNumber v-model="recommendation.recommended_budget_usd" mode="currency" currency="USD" locale="en-US" />
        </div>
      </div>

      <!-- 🎯 ADSET -->
      <h4 class="mt-4">🎯 Ad Set</h4>
      <div class="p-fluid formgrid grid">
        <div class="field col-12 md:col-6">
          <label>Ubicación</label>
          <InputText v-model="recommendation.target_audience.location" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Rango de edad</label>
          <InputText v-model="recommendation.target_audience.age_range" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Género</label>
          <InputText v-model="recommendation.target_audience.gender" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Idiomas</label>
          <InputText v-model="recommendation.target_audience.language" />
        </div>
      </div>

      <!-- 📣 AD -->
      <h4 class="mt-4">📣 Anuncio</h4>
      <div class="p-fluid formgrid grid">
        <div class="field col-12 md:col-6">
          <label>Título</label>
          <InputText v-model="recommendation.creative_recommendations.headline" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Texto principal</label>
          <Textarea v-model="recommendation.creative_recommendations.primary_text" rows="3" />
        </div>
        <div class="field col-12 md:col-6">
          <label>CTA (Llamado a la acción)</label>
          <InputText v-model="recommendation.creative_recommendations.cta" />
        </div>
      </div>

      <div class="flex gap-3 mt-5">
        <Button label="📤 Publicar en Meta" class="p-button-info" @click="publishCampaign" />

        <Button label="Guardar configuración" icon="pi pi-save" class="p-button-success" @click="saveConfig" />
        <Button label="Nueva recomendación" icon="pi pi-refresh" class="p-button-secondary" @click="resetForm" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/service/api';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';

const form = ref({
  business_type: '',
  objective: '',
  budget: null,
});
const recommendation = ref(null);
const objectives = [
  'Agendar citas',
  'Dejar datos de contacto',
  'Visita a página web',
  'Descargar aplicación',
  'Llamar al negocio',
];

async function generateRecommendation() {
  try {
    const { data } = await apiClient.post('/meta/optimize', form.value);

    const rec = data.recommendation || {};

    // 🔥 Previene error: rellena estructura mínima
    recommendation.value = {
      campaign_name: rec.campaign_name || "",
      objective: rec.objective || "",
      recommended_budget_usd: rec.recommended_budget_usd || 0,
      target_audience: {
        location: rec?.target_audience?.location || "",
        age_range: rec?.target_audience?.age_range || "",
        gender: rec?.target_audience?.gender || "",
               language: rec?.target_audience?.language || "",
        interests: rec?.target_audience?.interests || [],
        behaviors: rec?.target_audience?.behaviors || []
      },
      creative_recommendations: {
        headline: rec?.creative_recommendations?.headline || "",
        primary_text: rec?.creative_recommendations?.primary_text || "",
        cta: rec?.creative_recommendations?.cta || ""
      }
    };
  } catch (err) {
    console.error(err);
    alert("Error generando la recomendación.");
  }
}


function saveConfig() {
  console.log('Configuración final guardada:', recommendation.value);
  alert('Configuración almacenada (ver consola)');
}

function resetForm() {
  recommendation.value = null;
  form.value = { business_type: '', objective: '', budget: null };
}
async function publishCampaign() {
  try {
    const { data } = await apiClient.post('/meta/create-campaign', recommendation.value);
    alert(`✅ Campaña creada exitosamente.\nID: ${data.campaign_id}`);
  } catch (err) {
    console.error(err);
    alert(`❌ Error: ${err.response?.data?.detail || err.message}`);
  }
}
</script>
