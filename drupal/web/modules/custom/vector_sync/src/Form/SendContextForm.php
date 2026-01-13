<?php

namespace Drupal\vector_sync\Form;

use Drupal\Core\Form\FormBase;
use Drupal\Core\Form\FormStateInterface;
use Drupal\node\Entity\Node;

class SendContextForm extends FormBase {

  public function getFormId() {
    return 'vector_sync_send_context_form';
  }

  public function buildForm(array $form, FormStateInterface $form_state) {
    $form['description'] = [
      '#markup' => '<p>Send published Context nodes in batches to the configured endpoint.</p>',
    ];

    $form['batch_size'] = [
      '#type' => 'number',
      '#title' => $this->t('Batch size'),
      '#default_value' => 50,
      '#min' => 1,
      '#required' => TRUE,
    ];

    $form['submit'] = [
      '#type' => 'submit',
      '#value' => $this->t('Send nodes'),
    ];

    return $form;
  }

  public function submitForm(array &$form, FormStateInterface $form_state) {
    $batch_size = (int) $form_state->getValue('batch_size');

    $nids = \Drupal::entityQuery('node')
      ->condition('type', 'context')
      ->condition('status', 1)
      ->sort('changed', 'DESC')
      ->range(0, $batch_size)
      ->accessCheck(TRUE)
      ->execute();

    if (empty($nids)) {
      $this->messenger()->addWarning($this->t('No published Context nodes found.'));
      return;
    }

    $nodes = Node::loadMultiple($nids);
    $items = [];

    foreach ($nodes as $node) {
      $items[] = [
        'uuid' => $node->uuid(),
        'title' => $node->label(),
        'text' => $node->get('field_description')->value ?? '',
        'tags' => array_map(fn($t) => $t->label(), $node->get('field_tags')->referencedEntities()),
        'agents' => array_map(fn($t) => $t->label(), $node->get('field_agents')->referencedEntities()),
        'changed' => (int) $node->getChangedTime(),
      ];
    }

    $config = $this->config('vector_sync.settings');

    $payload = [
      'assistant_id' => 'vector_writer',
      'input' => ['items' => $items],
      'metadata' => [
        'source' => 'drupal',
        'content_type' => 'context',
        'batch_id' => 'sync-' . date('Y-m-d-His'),
      ],
      'on_completion' => 'delete',
    ];

    try {
      \Drupal::httpClient()->post(
        rtrim($config->get('endpoint_url'), '/') . '/runs/wait',
        [
          'headers' => [
            'Content-Type' => 'application/json',
            'X-Api-Key' => $config->get('api_key'),
          ],
          'json' => $payload,
        ]
      );

      $this->messenger()->addStatus(
        $this->t('Successfully sent @count context nodes.', ['@count' => count($items)])
      );
    }
    catch (\Throwable $e) {
      $this->messenger()->addError($this->t('Send failed: @msg', ['@msg' => $e->getMessage()]));
    }
  }
}
