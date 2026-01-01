<?php

namespace Drupal\vector_sync\Form;

use Drupal\Core\Form\ConfigFormBase;
use Drupal\Core\Form\FormStateInterface;

class SettingsForm extends ConfigFormBase {

  protected function getEditableConfigNames() {
    return ['vector_sync.settings'];
  }

  public function getFormId() {
    return 'vector_sync_settings_form';
  }

  public function buildForm(array $form, FormStateInterface $form_state) {
    $config = $this->config('vector_sync.settings');

    $form['api_key'] = [
      '#type' => 'textfield',
      '#title' => $this->t('API Key'),
      '#default_value' => $config->get('api_key'),
      '#required' => TRUE,
    ];

    $form['endpoint_url'] = [
      '#type' => 'textfield',
      '#title' => $this->t('Endpoint URL'),
      '#default_value' => $config->get('endpoint_url'),
      '#required' => TRUE,
    ];

    return parent::buildForm($form, $form_state);
  }

  public function submitForm(array &$form, FormStateInterface $form_state) {
    $this->config('vector_sync.settings')
      ->set('api_key', $form_state->getValue('api_key'))
      ->set('endpoint_url', $form_state->getValue('endpoint_url'))
      ->save();

    parent::submitForm($form, $form_state);
  }

}
