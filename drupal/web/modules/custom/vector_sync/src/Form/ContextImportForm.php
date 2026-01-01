<?php

namespace Drupal\vector_sync\Form;

use Drupal\Core\Form\FormBase;
use Drupal\Core\Form\FormStateInterface;
use Drupal\node\Entity\Node;
use Drupal\taxonomy\Entity\Term;

class ContextImportForm extends FormBase {

  public function getFormId() {
    return 'vector_sync_import_form';
  }

  public function buildForm(array $form, FormStateInterface $form_state) {
    $form['json_payload'] = [
      '#type' => 'textarea',
      '#title' => $this->t('JSON Payload'),
      '#description' => $this->t('Paste the JSON payload with "items".'),
      '#rows' => 15,
      '#required' => TRUE,
    ];

    $form['submit'] = [
      '#type' => 'submit',
      '#value' => $this->t('Import Items'),
    ];

    return $form;
  }

  public function submitForm(array &$form, FormStateInterface $form_state) {
    $json = $form_state->getValue('json_payload');
    $data = json_decode($json, TRUE);

    if (!isset($data['items']) || !is_array($data['items'])) {
      $this->messenger()->addError($this->t('Invalid JSON structure.'));
      return;
    }

    $created = 0;
    $updated = 0;

    foreach ($data['items'] as $item) {
      $title = $item['title'] ?? '';
      $desc = $item['text'] ?? '';
      $tags = $item['tags'] ?? [];
      $agents = $item['agents'] ?? [];

      $tag_entities = $this->getOrCreateTerms($tags, 'generic_tags');
      $agent_entities = $this->getOrCreateTerms($agents, 'agents');

      $hash = $this->generateHash($agent_entities, $tag_entities, $title, $desc);

      $nids = \Drupal::entityQuery('node')
        ->condition('type', 'context')
        ->condition('field_hash', $hash)
        ->accessCheck()
        ->execute();

      if (!empty($nids)) {
        $node = Node::load(reset($nids));
        $updated++;
      } else {
        $node = Node::create(['type' => 'context']);
        $created++;
      }

      $node->setTitle($title);
      $node->set('field_description', $desc);
      $node->set('field_agents', array_map(fn($term) => $term->id(), $agent_entities));
      $node->set('field_tags', array_map(fn($term) => $term->id(), $tag_entities));
      $node->set('field_hash', $hash);
      $node->setNewRevision(TRUE);
      $node->save();
    }

    $this->messenger()->addStatus($this->t('Import complete. @c created, @u updated.', [
      '@c' => $created,
      '@u' => $updated,
    ]));
  }

  private function getOrCreateTerms(array $names, string $vocabulary) {
    $terms = [];
    foreach ($names as $name) {
      $query = \Drupal::entityTypeManager()->getStorage('taxonomy_term')->getQuery();
      $query->condition('vid', $vocabulary);
      $query->condition('name', $name);
      $query->accessCheck();
      $tids = $query->execute();

      if (!empty($tids)) {
        $term = Term::load(reset($tids));
      }
      else {
        $term = Term::create([
          'vid' => $vocabulary,
          'name' => $name,
        ]);
        $term->save();
      }
      $terms[] = $term;
    }
    return $terms;
  }

  private function generateHash(array $agents, array $tags, string $title, string $desc) {
    $agent_keys = array_map(fn($term) => strtolower($term->label()), $agents);
    $tag_keys = array_map(fn($term) => strtolower($term->label()), $tags);

    sort($agent_keys);
    sort($tag_keys);

    $title = trim(strtolower(strip_tags($title)));
    $desc = trim(strtolower(strip_tags($desc)));

    $source_string = implode('|', [
      implode(',', $agent_keys),
      implode(',', $tag_keys),
      $title,
      $desc,
    ]);

    return hash('sha256', $source_string);
  }
}
