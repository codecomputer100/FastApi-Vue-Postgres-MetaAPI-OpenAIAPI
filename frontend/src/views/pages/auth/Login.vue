<template>
  <div class="flex flex-col items-center justify-center h-screen bg-gray-50">
    <Card class="w-96 shadow-md">
      <template #title>Inicia sesión</template>
      <template #content>
        <p>Conéctate con tu cuenta de Facebook para continuar.</p>
        <Button
          label="Iniciar sesión con Facebook"
          icon="pi pi-facebook"
          class="w-full mt-3"
          @click="handleLogin"
        />
      </template>
    </Card>
  </div>
</template>

<script setup>
import { loginWithFacebook } from '@/service/authService';
import Button from 'primevue/button';
import Card from 'primevue/card';

function handleLogin() {
  loginWithFacebook();
}
</script>
